import React, { useState } from 'react';
import { X, Minus, Plus, Trash2, ShoppingCart } from 'lucide-react';

interface SalesItem {
  id: number;
  name: string;
  quantity: number;
  price: number;
  stock: number;
}

interface SalesDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToPayment: (total: number) => void;
  cartItems: SalesItem[];
  updateCartItemQuantity: (id: number, change: number) => void;
  removeCartItem: (id: number) => void;
  clearCart: () => void;
}

const SalesDrawer: React.FC<SalesDrawerProps> = ({ isOpen, onClose, onNavigateToPayment, cartItems, updateCartItemQuantity, removeCartItem, clearCart }) => {
  const [isAdjustableAmount, setIsAdjustableAmount] = useState(false);
  const [customAmount, setCustomAmount] = useState('');
  const [internalNote, setInternalNote] = useState('');

  const subtotal = cartItems.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  const tax = subtotal * 0.15; // 15% tax
  const total = subtotal + tax;

  const handlePaymentClick = () => {
    onNavigateToPayment(total);
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-y-0 right-0 w-full sm:w-96 bg-bg-surface border-l border-divider transform transition-transform duration-300 ease-in-out z-30 ${
      isOpen ? 'translate-x-0' : 'translate-x-full'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-divider bg-bg-surface">
        <h2 className="text-lg font-semibold text-text-primary animate-slide-in-left">
          Shopping Cart
        </h2>
        <button 
          onClick={onClose}
          className="p-2 hover:bg-gray-50 rounded-full transition-all duration-300 hover:scale-110 icon-bounce"
        >
          <X size={20} className="text-text-primary" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {cartItems.length > 0 ? (
          <div className="space-y-4 animate-stagger">
            {cartItems.map((item) => (
              <div 
                key={item.id} 
                className="bg-white p-4 rounded-lg border border-divider shadow-sm hover-lift"
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-text-primary text-glow">{item.name}</h3>
                  <button 
                    onClick={() => removeCartItem(item.id)}
                    className="text-error hover:text-error-600 transition-colors duration-300 icon-bounce"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <button 
                      onClick={() => updateCartItemQuantity(item.id, -1)}
                      disabled={item.quantity <= 1}
                      className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-110 flex items-center justify-center"
                    >
                      <Minus size={14} />
                    </button>
                    <span className="w-8 text-center font-medium text-text-primary">{item.quantity}</span>
                    <button 
                      onClick={() => updateCartItemQuantity(item.id, 1)}
                      disabled={item.quantity >= item.stock}
                      className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-110 flex items-center justify-center"
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-text-primary">${(item.price * item.quantity).toFixed(2)}</div>
                    <div className="text-sm text-text-secondary">${item.price.toFixed(2)} each</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 animate-fade-in">
            <ShoppingCart size={48} className="text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-text-primary mb-2">Your cart is empty</h3>
            <p className="text-text-secondary">Add some products to get started</p>
          </div>
        )}

        {/* Summary */}
        {cartItems.length > 0 && (
          <div className="mt-6 space-y-4 animate-fade-in">
            {/* Subtotal */}
            <div className="bg-gray-50 p-4 rounded-lg border border-divider">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Subtotal:</span>
                  <span className="text-text-primary">${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-text-secondary">Tax (15%):</span>
                  <span className="text-text-primary">${tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold border-t border-divider pt-2">
                  <span className="text-text-primary">Total:</span>
                  <span className="text-success">${total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* Payment Button */}
            <button
              onClick={handlePaymentClick}
              className="w-full bg-complement hover:bg-complement-700 text-white font-medium py-4 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-lg btn-animate"
            >
              Proceed to Payment
            </button>

            {/* Clear Cart */}
            <button
              onClick={clearCart}
              className="w-full bg-gray-100 hover:bg-gray-200 text-text-primary font-medium py-3 rounded-lg transition-all duration-300"
            >
              Clear Cart
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SalesDrawer;