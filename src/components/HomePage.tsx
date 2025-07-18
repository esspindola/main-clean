import React, { useState, useMemo, useEffect } from 'react';
import { Search, RefreshCw, ShoppingCart } from 'lucide-react';
import ProductCard from './ProductCard';
import SalesDrawer from './SalesDrawer';
import PaymentScreen from './PaymentScreen';
import PaymentSuccessScreen from './PaymentSuccessScreen';
import { productsAPI, salesAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface HomePageProps {
  searchTerm?: string;
}

interface Product {
  id: number;
  name: string;
  description?: string;
  sku?: string;
  category: string;
  stock: number;
  price: number;
  status: 'active' | 'inactive';
  image?: string;
}

const HomePage: React.FC<HomePageProps> = ({ searchTerm: externalSearchTerm = '' }) => {
  const { isAuthenticated } = useAuth();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isPaymentOpen, setIsPaymentOpen] = useState(false);
  const [isSuccessOpen, setIsSuccessOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [paymentTotal, setPaymentTotal] = useState<number>(0);
  const [paymentMethod, setPaymentMethod] = useState<string>('');
  const [localSearchTerm, setLocalSearchTerm] = useState<string>('');
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Carrito de compras
  interface CartItem {
    id: number;
    name: string;
    price: number;
    stock: number;
    quantity: number;
  }
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

  // Use local search term (takes priority over external)
  const activeSearchTerm = localSearchTerm || externalSearchTerm;

  // Fetch products from backend
  useEffect(() => {
    const fetchProducts = async () => {
      if (!isAuthenticated) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await productsAPI.getAll();
        if (response.success) {
          // Mostrar productos activos (permitir stock 0 para ver todos los productos)
          const availableProducts = response.products.filter(
            (product: Product) => product.status === 'active'
          );
          console.log('Productos cargados:', response.products);
          console.log('Productos disponibles:', availableProducts);
          setProducts(availableProducts);
        } else {
          setError('Error al cargar los productos');
        }
      } catch (err) {
        console.error('Error fetching products:', err);
        setError('Error al cargar los productos');
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [isAuthenticated]);

  // Actualizar productos cuando la página se vuelve visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && isAuthenticated) {
        handleRefreshProducts();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isAuthenticated]);

  // Filter products based on search term
  const filteredProducts = useMemo(() => {
    if (!activeSearchTerm.trim()) {
      return products;
    }
    
    return products.filter(product =>
      product.name.toLowerCase().includes(activeSearchTerm.toLowerCase())
    );
  }, [activeSearchTerm, products]);

  // Al hacer click en un producto, agregarlo al carrito
  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
    setIsDrawerOpen(true);
    setCartItems(prevCart => {
      const existing = prevCart.find(item => item.id === product.id);
      if (existing) {
        // Sumar cantidad, respetando el stock
        return prevCart.map(item =>
          item.id === product.id
            ? { ...item, quantity: Math.min(item.quantity + 1, product.stock) }
            : item
        );
      } else {
        return [
          ...prevCart,
          {
            id: product.id,
            name: product.name,
            price: product.price,
            stock: product.stock,
            quantity: 1,
          },
        ];
      }
    });
  };

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false);
  };

  const handleNavigateToPayment = (total: number) => {
    setPaymentTotal(total);
    setIsPaymentOpen(true);
  };

  const handleBackFromPayment = () => {
    setIsPaymentOpen(false);
  };

  const handlePaymentSuccess = async (method: string) => {
    try {
      // Preparar los datos de la venta
      const saleData = {
        items: cartItems.map(item => ({
          productId: item.id,
          quantity: item.quantity,
          price: item.price
        })),
        total: paymentTotal,
        paymentMethod: method
      };

      // Enviar la venta al backend
      const saleResponse = await salesAPI.create(saleData);
      
      if (saleResponse.success) {
        console.log('Venta creada exitosamente:', saleResponse);
        
        // Actualizar el inventario local inmediatamente
        setProducts(prevProducts => 
          prevProducts.map(product => {
            const cartItem = cartItems.find(item => item.id === product.id);
            if (cartItem) {
              return {
                ...product,
                stock: Math.max(0, product.stock - cartItem.quantity)
              };
            }
            return product;
          })
        );

        // Mostrar mensaje de éxito
        setPaymentMethod(method);
        setIsPaymentOpen(false);
        setIsSuccessOpen(true);
      } else {
        console.error('Error al crear la venta:', saleResponse);
        alert('Error al procesar la venta. Por favor, intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error al procesar la venta:', error);
      alert('Error al procesar la venta. Por favor, intenta de nuevo.');
    }
  };

  const handleNewOrder = () => {
    // Reset all states to start fresh
    setIsSuccessOpen(false);
    setIsDrawerOpen(false);
    setIsPaymentOpen(false);
    setSelectedProduct(null);
    setPaymentTotal(0);
    setPaymentMethod('');
    // Reset cart items to initial state
    setCartItems([]);
  };

  const handleLocalSearchChange = (value: string) => {
    setLocalSearchTerm(value);
  };

  // Modificar cantidad de un producto en el carrito
  const updateCartItemQuantity = (id: number, change: number) => {
    setCartItems(prevCart =>
      prevCart.map(item =>
        item.id === id
          ? { ...item, quantity: Math.max(1, Math.min(item.quantity + change, item.stock)) }
          : item
      )
    );
  };

  // Eliminar producto del carrito
  const removeCartItem = (id: number) => {
    setCartItems(prevCart => prevCart.filter(item => item.id !== id));
  };

  // Limpiar carrito
  const clearCart = () => {
    setCartItems([]);
  };

  // Función para recargar productos
  const handleRefreshProducts = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      setError(null);
      const response = await productsAPI.getAll();
      if (response.success) {
        // Mostrar productos activos (permitir stock 0 para ver todos los productos)
        const availableProducts = response.products.filter(
          (product: Product) => product.status === 'active'
        );
        console.log('Productos recargados:', response.products);
        console.log('Productos disponibles:', availableProducts);
        setProducts(availableProducts);
      } else {
        setError('Error al recargar los productos');
      }
    } catch (err) {
      console.error('Error refreshing products:', err);
      setError('Error al recargar los productos');
    } finally {
      setLoading(false);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-bg-main pt-16 flex items-center justify-center animate-fade-in">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4 animate-pulse-glow"></div>
          <p className="text-text-secondary animate-slide-in-left">Cargando productos...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-bg-main pt-16 flex items-center justify-center animate-fade-in">
        <div className="text-center">
          <div className="text-red-500 mb-4 animate-bounce-in">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <p className="text-text-primary mb-4 animate-slide-in-left">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-primary hover:bg-primary-600 text-black font-medium px-4 py-2 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg btn-animate"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className={`py-8 transition-all duration-300 ${
        isDrawerOpen && !isPaymentOpen && !isSuccessOpen ? 'md:mr-[40%] lg:mr-[33.333333%]' : ''
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            {/* Title and Search Row */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-2">
              <h1 className="text-2xl font-bold text-text-primary animate-slide-in-left">
                Tablero de Venta
              </h1>
              
              {/* Search and Refresh Row */}
              <div className="flex items-center gap-3">
                {/* Search Bar */}
                <div className="relative w-full sm:w-80 animate-slide-in-left">
                  <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary icon-bounce" />
                  <input
                    type="text"
                    value={localSearchTerm}
                    onChange={(e) => handleLocalSearchChange(e.target.value)}
                    placeholder="Buscar productos..."
                    className="w-full pl-10 pr-4 py-2 border border-divider rounded-lg text-sm focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary placeholder-text-secondary transition-all duration-300 hover:border-complement/50"
                  />
                </div>
                
                {/* Refresh Button */}
                <button
                  onClick={handleRefreshProducts}
                  disabled={loading}
                  className="p-2 bg-primary hover:bg-primary-600 text-black rounded-lg transition-all duration-300 hover:scale-110 hover:shadow-lg icon-bounce disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Actualizar productos"
                >
                  <RefreshCw size={20} className={`${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
            
            {/* Description */}
            <p className="text-text-secondary animate-slide-in-right">
              {activeSearchTerm ? (
                <>
                  Mostrando {filteredProducts.length} resultado{filteredProducts.length !== 1 ? 's' : ''} para "{activeSearchTerm}"
                </>
              ) : (
                'Selecciona productos para crear órdenes de venta rápidamente'
              )}
            </p>
          </div>

          {/* Responsive Grid with white background */}
          <div className="bg-white p-6 rounded-lg border border-divider animate-scale-in">
            {filteredProducts.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6 animate-stagger">
                {filteredProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onClick={handleProductClick}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 animate-fade-in">
                <div className="text-text-secondary mb-4 animate-bounce-in">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-text-primary mb-2 animate-slide-in-left">
                  No se encontraron productos
                </h3>
                <p className="text-text-secondary animate-slide-in-right">
                  {activeSearchTerm 
                    ? `No hay productos que coincidan con "${activeSearchTerm}". Intenta con otros términos de búsqueda.`
                    : 'No hay productos disponibles para la venta.'
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      <SalesDrawer 
        isOpen={isDrawerOpen && !isPaymentOpen && !isSuccessOpen}
        onClose={handleCloseDrawer}
        onNavigateToPayment={handleNavigateToPayment}
        cartItems={cartItems}
        updateCartItemQuantity={updateCartItemQuantity}
        removeCartItem={removeCartItem}
        clearCart={clearCart}
      />

      <PaymentScreen
        isOpen={isPaymentOpen}
        onBack={handleBackFromPayment}
        onPaymentSuccess={handlePaymentSuccess}
        total={paymentTotal}
      />

      <PaymentSuccessScreen
        isOpen={isSuccessOpen}
        onNewOrder={handleNewOrder}
        paymentMethod={paymentMethod}
        total={paymentTotal}
        items={cartItems}
      />
    </>
  );
};

export default HomePage;