import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Package, Home, Plus, Archive, Brain, Settings, LogOut, User, Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const SideMenu: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [showLogout, setShowLogout] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const menuItems = [
    {
      name: 'Home',
      icon: Home,
      path: '/',
      description: 'Página principal'
    },
    {
      name: 'Nuevo Producto',
      icon: Plus,
      path: '/new-product',
      description: 'Agregar producto'
    },
    {
      name: 'Inventario',
      icon: Archive,
      path: '/inventory',
      description: 'Ver inventario'
    },
    {
      name: 'Smart Inventory',
      icon: Brain,
      path: '/smart-inventory',
      description: 'IA para inventario'
    }
  ];

  const bottomMenuItems = [
    {
      name: 'Configuraciones',
      icon: Settings,
      path: '/profile',
      description: 'Ajustes'
    }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    // Cerrar menú móvil después de navegar
    setIsMobileMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Componente para renderizar los elementos del menú
  const renderMenuItems = (items: typeof menuItems, className: string = '') => {
    return items.map((item) => {
      const Icon = item.icon;
      const isActive = location.pathname === item.path;
      
      return (
        <button
          key={item.path}
          onClick={() => handleNavigation(item.path)}
          className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors group ${className} ${
            isActive
              ? 'bg-complement-50 text-complement-700 border border-complement-200'
              : 'text-text-secondary hover:bg-gray-50 hover:text-text-primary'
          }`}
        >
          <Icon 
            size={20} 
            className={`mr-3 ${
              isActive ? 'text-complement-600' : 'text-text-secondary group-hover:text-text-primary'
            }`} 
          />
          <div className="flex-1">
            <div className={`font-medium ${
              isActive ? 'text-complement-700' : 'text-text-primary'
            }`}>
              {item.name}
            </div>
            <div className="text-xs text-text-secondary">
              {item.description}
            </div>
          </div>
        </button>
      );
    });
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={toggleMobileMenu}
          className="p-2 bg-bg-surface border border-divider rounded-lg shadow-lg hover:bg-gray-50 transition-colors"
        >
          {isMobileMenuOpen ? (
            <X size={24} className="text-text-primary" />
          ) : (
            <Menu size={24} className="text-text-primary" />
          )}
        </button>
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Menu Sidebar */}
      <div className={`md:hidden fixed inset-y-0 left-0 w-64 bg-bg-surface border-r border-divider z-50 transform transition-transform duration-300 ease-in-out ${
        isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Logo/Brand */}
        <div className="flex items-center justify-center h-16 px-6 border-b border-divider">
          <img 
            src="/image/logo.png" 
            alt="FrontPOSw Logo" 
            className="h-10 w-auto"
          />
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
          {renderMenuItems(menuItems)}
        </nav>

        {/* Bottom Navigation */}
        <div className="px-4 py-4 border-t border-divider space-y-2">
          {renderMenuItems(bottomMenuItems)}
        </div>

        {/* User Info */}
        <div className="px-4 py-4 border-t border-divider">
          <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50">
            <div className="w-8 h-8 bg-complement rounded-full flex items-center justify-center">
              <User size={16} className="text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-text-primary truncate">
                {user?.fullName || 'Usuario'}
              </div>
              <div className="text-xs text-text-secondary truncate">
                {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-error hover:bg-error-50 rounded-lg transition-colors"
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Desktop Side Menu */}
      <div className="hidden md:flex md:flex-col md:fixed md:inset-y-0 md:left-0 md:w-64 md:bg-bg-surface md:border-r md:border-divider md:z-40">
        {/* Logo/Brand */}
        <div className="flex items-center justify-center h-16 px-6 border-b border-divider">
          <img 
            src="/image/logo.png" 
            alt="FrontPOSw Logo" 
            className="h-10 w-auto"
          />
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {renderMenuItems(menuItems)}
        </nav>

        {/* Bottom Navigation */}
        <div className="px-4 py-4 border-t border-divider space-y-2">
          {renderMenuItems(bottomMenuItems)}
        </div>

        {/* User Info with Hover Animation */}
        <div className="px-4 py-4 border-t border-divider">
          <div 
            className="relative cursor-pointer"
            onMouseEnter={() => setShowLogout(true)}
            onMouseLeave={() => setShowLogout(false)}
          >
            <div className={`flex items-center space-x-3 p-3 rounded-lg transition-all duration-300 ease-in-out ${
              showLogout 
                ? 'bg-error-50 border border-error-200 shadow-sm' 
                : 'hover:bg-gray-50'
            }`}>
              <div className="w-8 h-8 bg-complement rounded-full flex items-center justify-center">
                <User size={16} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-text-primary truncate">
                  {user?.fullName || 'Usuario'}
                </div>
                <div className="text-xs text-text-secondary truncate">
                  {user?.role === 'admin' ? 'Administrador' : 'Usuario'}
                </div>
              </div>
              
              {/* Logout Icon with Animation */}
              <div className={`transition-all duration-300 ease-in-out ${
                showLogout 
                  ? 'opacity-100 translate-x-0' 
                  : 'opacity-0 translate-x-2'
              }`}>
                <LogOut size={16} className="text-error" />
              </div>
            </div>

            {/* Logout Overlay with Animation */}
            <div className={`absolute inset-0 flex items-center justify-center rounded-lg transition-all duration-300 ease-in-out ${
              showLogout 
                ? 'opacity-100 bg-error-500 text-white shadow-lg transform scale-100' 
                : 'opacity-0 bg-transparent transform scale-95 pointer-events-none'
            }`}>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 font-medium text-sm"
              >
                <LogOut size={16} />
                <span>Cerrar sesión</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SideMenu;