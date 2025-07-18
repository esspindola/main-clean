import { API_CONFIG, ENDPOINTS } from '../config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

// Types
export interface User {
  id: number;
  email: string;
  fullName: string;
  role: 'admin' | 'user';
  phone?: string;
  address?: string;
}

export interface Product {
  id: number;
  name: string;
  description?: string;
  sku?: string;
  category: string;
  price: number;
  stock: number;
  status: 'active' | 'inactive';
  image?: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  token: string;
  user: User;
}

export interface ProductsResponse {
  success: boolean;
  products: Product[];
}

export interface ProductResponse {
  success: boolean;
  message: string;
  product: Product;
}

// Helper function to get auth token
const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

// Helper function to make API requests
const apiRequest = async <T>(endpoint: string, options: RequestInit = {}): Promise<T> => {
  const token = getAuthToken();
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

// Auth API
export const authAPI = {
  register: (userData: any): Promise<AuthResponse> => apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }),
  
  login: (credentials: { email: string; password: string }): Promise<AuthResponse> => apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }),
  
  logout: (): Promise<{ success: boolean; message: string }> => apiRequest('/auth/logout', {
    method: 'POST',
  }),
  
  getCurrentUser: (): Promise<{ success: boolean; user: User }> => apiRequest('/auth/me'),
  
  forgotPassword: (email: string): Promise<{ success: boolean; message: string }> => apiRequest('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  }),
  
  resetPassword: (token: string, password: string): Promise<{ success: boolean; message: string }> => apiRequest('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, password }),
  }),
};

// Products API
export const productsAPI = {
  getAll: (params: Record<string, any> = {}): Promise<ProductsResponse> => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/products?${queryString}`);
  },
  
  getById: (id: number): Promise<ProductResponse> => apiRequest(`/products/${id}`),
  
  create: (productData: Partial<Product>): Promise<ProductResponse> => apiRequest('/products', {
    method: 'POST',
    body: JSON.stringify(productData),
  }),
  
  update: (id: number, productData: Partial<Product>): Promise<ProductResponse> => apiRequest(`/products/${id}`, {
    method: 'PUT',
    body: JSON.stringify(productData),
  }),
  
  delete: (id: number): Promise<{ success: boolean; message: string; product: Product }> => apiRequest(`/products/${id}`, {
    method: 'DELETE',
  }),
  
  uploadImages: (id: number, formData: FormData): Promise<any> => {
    const token = getAuthToken();
    return fetch(`${API_BASE_URL}/products/${id}/images`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    });
  },
  
  getCategories: (): Promise<{ success: boolean; categories: string[] }> => apiRequest('/products/categories/list'),
};

// Inventory API
export const inventoryAPI = {
  getAll: (params: Record<string, any> = {}): Promise<any> => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/inventory?${queryString}`);
  },
  
  getLowStock: (): Promise<any> => apiRequest('/inventory/low-stock'),
  
  updateStock: (id: number, stockData: any): Promise<any> => apiRequest(`/inventory/${id}/stock`, {
    method: 'PUT',
    body: JSON.stringify(stockData),
  }),
  
  getMovements: (params: Record<string, any> = {}): Promise<any> => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/inventory/movements?${queryString}`);
  },
  
  bulkUpdate: (updates: any[]): Promise<any> => apiRequest('/inventory/bulk-update', {
    method: 'POST',
    body: JSON.stringify(updates),
  }),
  
  getStats: (): Promise<any> => apiRequest('/inventory/stats/summary'),
};

// Sales API
export const salesAPI = {
  getAll: (params: Record<string, any> = {}): Promise<any> => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/sales?${queryString}`);
  },
  
  getById: (id: number): Promise<any> => apiRequest(`/sales/${id}`),
  
  create: (saleData: any): Promise<any> => apiRequest('/sales', {
    method: 'POST',
    body: JSON.stringify(saleData),
  }),
  
  updateStatus: (id: number, status: string): Promise<any> => apiRequest(`/sales/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }),
  
  getStats: (params: Record<string, any> = {}): Promise<any> => {
    const queryString = new URLSearchParams(params).toString();
    return apiRequest(`/sales/stats/summary?${queryString}`);
  },
};

// Profile API
export const profileAPI = {
  get: (): Promise<{ success: boolean; user: User }> => apiRequest('/profile'),
  
  update: (profileData: Partial<User>): Promise<{ success: boolean; message: string; user: User }> => apiRequest('/profile', {
    method: 'PUT',
    body: JSON.stringify(profileData),
  }),
  
  changePassword: (passwordData: any): Promise<{ success: boolean; message: string }> => apiRequest('/profile/password', {
    method: 'PUT',
    body: JSON.stringify(passwordData),
  }),
  
  updateNotifications: (notificationData: any): Promise<any> => apiRequest('/profile/notifications', {
    method: 'PUT',
    body: JSON.stringify(notificationData),
  }),
  
  getSessions: (): Promise<any> => apiRequest('/profile/sessions'),
  
  closeSession: (sessionId: string): Promise<any> => apiRequest(`/profile/sessions/${sessionId}`, {
    method: 'DELETE',
  }),
  
  getStats: (): Promise<any> => apiRequest('/profile/stats'),
  
  exportData: (): Promise<any> => apiRequest('/profile/export'),
  
  deleteAccount: (password: string): Promise<any> => apiRequest('/profile', {
    method: 'DELETE',
    body: JSON.stringify({ password }),
  }),
};

// OCR API
export const ocrAPI = {
  processDocument: (file: File): Promise<any> => {
    const token = getAuthToken();
    const formData = new FormData();
    formData.append('document', file);
    
    return fetch(`${API_BASE_URL}/ocr/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    });
  },
}; 