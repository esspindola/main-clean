import React from 'react';
import { Package } from 'lucide-react';

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

interface ProductCardProps {
  product: Product;
  onClick: (product: Product) => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  const handleClick = () => {
    onClick(product);
  };

  return (
    <div 
      onClick={handleClick}
      className="group relative bg-white rounded-lg border border-divider overflow-hidden cursor-pointer transform transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-lg hover:border-complement/30 animate-fade-in"
      style={{
        animationDelay: `${product.id * 100}ms`
      }}
    >
      {/* Stock Badge */}
      <div className="absolute top-3 right-3 z-10">
        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium transition-all duration-300 ${
          product.stock > 10 
            ? 'bg-success-100 text-success-800 group-hover:bg-success-200' 
            : product.stock > 0 
            ? 'bg-warning-100 text-warning-800 group-hover:bg-warning-200' 
            : 'bg-error-100 text-error-800 group-hover:bg-error-200'
        }`}>
          <div className={`w-2 h-2 rounded-full mr-1 transition-all duration-300 ${
            product.stock > 10 
              ? 'bg-success-500' 
              : product.stock > 0 
              ? 'bg-warning-500' 
              : 'bg-error-500'
          }`}></div>
          {product.stock} en stock
        </span>
      </div>

      {/* Product Image */}
      <div className="relative h-48 bg-gray-100 overflow-hidden group-hover:bg-gray-50 transition-colors duration-300">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover transform transition-transform duration-500 group-hover:scale-110"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <div className="text-gray-400 group-hover:text-gray-500 transition-colors duration-300">
              <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        )}
        
        {/* Overlay on hover */}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-300"></div>
      </div>

      {/* Product Info */}
      <div className="p-4 space-y-3">
        {/* Category */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium text-text-secondary uppercase tracking-wide group-hover:text-complement transition-colors duration-300">
            {product.category}
          </span>
          {product.sku && (
            <span className="text-xs text-text-secondary group-hover:text-text-primary transition-colors duration-300">
              {product.sku}
            </span>
          )}
        </div>

        {/* Product Name */}
        <h3 className="text-lg font-semibold text-text-primary group-hover:text-complement transition-colors duration-300 line-clamp-2">
          {product.name}
        </h3>

        {/* Description */}
        {product.description && (
          <p className="text-sm text-text-secondary line-clamp-2 group-hover:text-text-primary transition-colors duration-300">
            {product.description}
          </p>
        )}

        {/* Price and Action */}
        <div className="flex items-center justify-between pt-2">
          <div className="flex flex-col">
            <span className="text-2xl font-bold text-text-primary group-hover:text-complement transition-colors duration-300">
              ${product.price.toFixed(2)}
            </span>
            <span className="text-xs text-text-secondary group-hover:text-text-primary transition-colors duration-300">
              por unidad
            </span>
          </div>
          
          {/* Add to Cart Button */}
          <button className="opacity-0 group-hover:opacity-100 transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 ease-out bg-complement hover:bg-complement-600 text-white px-4 py-2 rounded-lg font-medium text-sm shadow-lg hover:shadow-xl">
            Agregar
          </button>
        </div>
      </div>

      {/* Click indicator */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-complement/20 rounded-lg transition-all duration-300 pointer-events-none"></div>
    </div>
  );
};

export default ProductCard;