// Configuración de la API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:4444/api';

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  TIMEOUT: 10000,
  HEADERS: {
    'Content-Type': 'application/json',
  }
};

// Endpoints
export const ENDPOINTS = {
  // Auth
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  LOGOUT: '/auth/logout',
  PROFILE: '/auth/profile',
  
  // Products
  PRODUCTS: '/products',
  PRODUCT_BY_ID: (id: number) => `/products/${id}`,
  
  // Sales
  SALES: '/sales',
  SALE_BY_ID: (id: number) => `/sales/${id}`,
  
  // Inventory
  INVENTORY: '/inventory',
  INVENTORY_MOVEMENTS: '/inventory/movements',
  
  // OCR
  OCR_UPLOAD: '/ocr/upload',
};

export default API_CONFIG; 