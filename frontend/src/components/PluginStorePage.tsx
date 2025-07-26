import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { usePlugins } from '../contexts/PluginContext';

interface IPlugin {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  status: 'active' | 'inactive' | 'coming-soon';
  version: string;
  author: string;
  rating: number;
  installs: number;
  price: 'free' | 'premium';
  features: string[];
  screenshot?: string;
}

const PluginStorePage: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { isPluginActive, togglePlugin } = usePlugins();
  const [plugins, setPlugins] = useState<IPlugin[]>([]);
  const [filteredPlugins, setFilteredPlugins] = useState<IPlugin[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);
  const categoriesRef = useRef<HTMLDivElement>(null);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState<'success' | 'info'>('info');

  const categories = [
    { id: 'all', name: 'Discover', icon: '🌟' },
    { id: 'productivity', name: 'Files & Productivity', icon: '📁' },
    { id: 'inventory', name: 'Inventory', icon: '📦' },
    { id: 'sales', name: 'Sales', icon: '💰' },
    { id: 'analytics', name: 'Analytics', icon: '📊' },
    { id: 'automation', name: 'Automation', icon: '⚡' },
    { id: 'integrations', name: 'Integrations', icon: '🔗' },
    { id: 'developer', name: 'Developer Tools', icon: '🛠️' },
  ];

  // Mock data for plugins
  const mockPlugins: IPlugin[] = [
    {
      id: 'ocr-module',
      name: 'OCR Document Scanner',
      description: 'Scan and extract data from invoices, receipts, and documents automatically',
      category: 'productivity',
      icon: '🔍',
      status: 'active',
      version: '1.2.0',
      author: 'ZatoBox Team',
      rating: 4.8,
      installs: 1250,
      price: 'free',
      features: ['Document scanning', 'Data extraction', 'Invoice processing', 'Receipt management'],
      screenshot: 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=400&h=300&fit=crop',
    },
    {
      id: 'smart-inventory',
      name: 'Smart Inventory Manager',
      description: 'Advanced inventory tracking with AI-powered stock predictions and alerts',
      category: 'inventory',
      icon: '🧠',
      status: 'coming-soon',
      version: '2.1.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'premium',
      features: ['AI predictions', 'Low stock alerts', 'Demand forecasting', 'Automated reordering'],
      screenshot: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=300&fit=crop',
    },
    {
      id: 'advanced-analytics',
      name: 'Advanced Analytics Dashboard',
      description: 'Comprehensive business analytics with real-time insights and reporting',
      category: 'analytics',
      icon: '📈',
      status: 'coming-soon',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'premium',
      features: ['Real-time dashboards', 'Custom reports', 'Data visualization', 'Export capabilities'],
    },
    {
      id: 'pos-integration',
      name: 'POS System Integration',
      description: 'Connect with popular POS systems for seamless data synchronization',
      category: 'integrations',
      icon: '💳',
      status: 'active',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 4.7,
      installs: 850,
      price: 'free',
      features: ['Multi-POS support', 'Real-time sync', 'Payment processing', 'Receipt printing'],
    },
    {
      id: 'email-automation',
      name: 'Email Automation Suite',
      description: 'Automate customer communications and marketing campaigns',
      category: 'automation',
      icon: '📧',
      status: 'coming-soon',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'premium',
      features: ['Email templates', 'Automated campaigns', 'Customer segmentation', 'Performance tracking'],
    },
    {
      id: 'mobile-app',
      name: 'Mobile App Companion',
      description: 'Native mobile app for managing your business on the go',
      category: 'productivity',
      icon: '📱',
      status: 'coming-soon',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'free',
      features: ['Offline mode', 'Push notifications', 'Barcode scanning', 'Quick actions'],
    },
    {
      id: 'api-gateway',
      name: 'API Gateway',
      description: 'Developer tools for custom integrations and third-party connections',
      category: 'developer',
      icon: '🔌',
      status: 'coming-soon',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'premium',
      features: ['REST API', 'Webhooks', 'OAuth support', 'Rate limiting'],
    },
    {
      id: 'multi-store',
      name: 'Multi-Store Manager',
      description: 'Manage multiple store locations from a single dashboard',
      category: 'inventory',
      icon: '🏪',
      status: 'coming-soon',
      version: '1.0.0',
      author: 'ZatoBox Team',
      rating: 0,
      installs: 0,
      price: 'premium',
      features: ['Store management', 'Inventory sync', 'Centralized reporting', 'Role-based access'],
    },
  ];

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      // Sync plugin status with context
      const syncedPlugins = mockPlugins.map(plugin => {
        // Keep coming-soon plugins as coming-soon
        if (plugin.status === 'coming-soon') {
          return plugin;
        }
        // For other plugins, sync with context
        return {
          ...plugin,
          status: (isPluginActive(plugin.id) ? 'active' : 'inactive') as 'active' | 'inactive' | 'coming-soon',
        };
      });

      setPlugins(syncedPlugins);
      setFilteredPlugins(syncedPlugins);
      setLoading(false);
    }, 1000);
  }, [isPluginActive]);

  useEffect(() => {
    let filtered = plugins;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(plugin => plugin.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(plugin =>
        plugin.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        plugin.description.toLowerCase().includes(searchQuery.toLowerCase()),
      );
    }

    setFilteredPlugins(filtered);
  }, [plugins, selectedCategory, searchQuery]);

  // Functions for horizontal scrolling
  const checkScrollButtons = () => {
    if (categoriesRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = categoriesRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  const scrollLeft = () => {
    if (categoriesRef.current) {
      categoriesRef.current.scrollBy({ left: -200, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (categoriesRef.current) {
      categoriesRef.current.scrollBy({ left: 200, behavior: 'smooth' });
    }
  };

  // Effect to check scroll buttons on mount and resize
  useEffect(() => {
    checkScrollButtons();
    window.addEventListener('resize', checkScrollButtons);

    // Check scroll buttons after a short delay to ensure DOM is ready
    const timeoutId = setTimeout(checkScrollButtons, 100);

    return () => {
      window.removeEventListener('resize', checkScrollButtons);
      clearTimeout(timeoutId);
    };
  }, []);

  // Effect to update scroll buttons when filtered plugins change
  useEffect(() => {
    const timeoutId = setTimeout(checkScrollButtons, 50);
    return () => clearTimeout(timeoutId);
  }, [filteredPlugins]);

  // Function to show notification
  const showPluginNotification = (message: string, type: 'success' | 'info') => {
    // Only show notifications when explicitly called, not automatically
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);

    setTimeout(() => {
      setShowNotification(false);
    }, 3000);
  };

  const handlePluginToggle = async(pluginId: string) => {
    if (!token) {
      alert('Please log in to manage plugins');
      return;
    }

    // Get current plugin info
    const plugin = plugins.find(p => p.id === pluginId);
    if (!plugin) {return;}

    // Toggle plugin status using context
    togglePlugin(pluginId);

    // Update local state to reflect the change
    setPlugins(prev => prev.map(p => {
      if (p.id === pluginId) {
        const newStatus = isPluginActive(pluginId) ? 'active' : 'inactive';
        return { ...p, status: newStatus as 'active' | 'inactive' | 'coming-soon' };
      }
      return p;
    }));

    // Plugin status updated successfully
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
    case 'active':
      return <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Active</span>;
    case 'inactive':
      return <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Inactive</span>;
    case 'coming-soon':
      return <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">Coming Soon</span>;
    default:
      return null;
    }
  };

  const getPriceBadge = (price: string) => {
    return price === 'free'
      ? <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Free</span>
      : <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">Premium</span>;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg-main flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading Plugin Store...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg-main">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-divider">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-text-primary">Plugin Store</h1>
              <p className="text-text-secondary text-sm hidden md:block">
                Browse the ever-growing collection of business modules on ZatoBox
              </p>
            </div>

          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between space-y-6 xl:space-y-0">
            {/* Search Section */}
            <div className="flex-1 xl:max-w-2xl animate-slide-in-left">
              <div className="relative plugin-store-search">
                <Search size={20} className="absolute left-6 top-1/2 transform -translate-y-1/2 text-text-secondary icon-bounce" />
                <input
                  type="text"
                  placeholder="Search plugins..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-16 pr-8 py-5 border border-divider rounded-lg text-sm focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary placeholder-text-secondary transition-all duration-300 hover:border-complement/50 shadow-sm"
                />
              </div>
            </div>

            {/* Category Tabs with Horizontal Scroll */}
            <div className="relative flex-1 xl:flex-none">
              <div className="relative">
                {/* Left Arrow */}
                {canScrollLeft && (
                  <button
                    onClick={scrollLeft}
                    className="absolute left-0 top-1/2 transform -translate-y-1/2 z-10 w-8 h-8 bg-white border border-divider rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-all duration-200 hover:scale-110"
                  >
                    <ChevronLeft size={16} className="text-text-primary" />
                  </button>
                )}

                {/* Right Arrow */}
                {canScrollRight && (
                  <button
                    onClick={scrollRight}
                    className="absolute right-0 top-1/2 transform -translate-y-1/2 z-10 w-8 h-8 bg-white border border-divider rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 transition-all duration-200 hover:scale-110"
                  >
                    <ChevronRight size={16} className="text-text-primary" />
                  </button>
                )}

                {/* Categories Container */}
                <div
                  ref={categoriesRef}
                  onScroll={checkScrollButtons}
                  className="flex gap-3 overflow-x-auto scrollbar-hide px-2 py-1 category-scroll-container"
                  style={{
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none',
                  }}
                >
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => setSelectedCategory(category.id)}
                      className={`flex-shrink-0 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-300 whitespace-nowrap category-tab ${
                        selectedCategory === category.id
                          ? 'active shadow-md transform scale-105'
                          : 'bg-gray-100 text-text-secondary hover:bg-gray-200 hover:shadow-sm'
                      }`}
                    >
                      <span className="mr-2">{category.icon}</span>
                      {category.name}
                    </button>
                  ))}
                </div>

                {/* Gradient Overlay for Right Edge */}
                <div className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-white to-transparent pointer-events-none"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Featured Section */}
        {selectedCategory === 'all' && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-text-primary mb-4">🔥 MOST INSTALLS By popular demand</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredPlugins.slice(0, 3).map((plugin) => (
                <div key={plugin.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  {plugin.screenshot && (
                    <div className="h-48 bg-gray-200 overflow-hidden">
                      <img
                        src={plugin.screenshot}
                        alt={plugin.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <span className="text-3xl">{plugin.icon}</span>
                        <div>
                          <h3 className="text-lg font-semibold text-text-primary">{plugin.name}</h3>
                          <p className="text-sm text-text-secondary">{plugin.description}</p>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(plugin.status)}
                        {getPriceBadge(plugin.price)}
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-yellow-400">⭐</span>
                        <span className="text-sm text-text-secondary">{plugin.rating}</span>
                        <span className="text-sm text-text-secondary">({plugin.installs})</span>
                      </div>
                    </div>
                    {plugin.status === 'active' ? (
                      <button
                        onClick={() => handlePluginToggle(plugin.id)}
                        className="w-full bg-red-100 text-red-800 py-2 px-4 rounded-lg font-medium hover:bg-red-200 transition-colors"
                      >
                        Deactivate
                      </button>
                    ) : plugin.status === 'inactive' ? (
                      <button
                        onClick={() => handlePluginToggle(plugin.id)}
                        className="w-full bg-green-100 text-green-800 py-2 px-4 rounded-lg font-medium hover:bg-green-200 transition-colors"
                      >
                        Activate
                      </button>
                    ) : (
                      <button
                        disabled
                        className="w-full bg-gray-100 text-gray-400 py-2 px-4 rounded-lg font-medium cursor-not-allowed"
                      >
                        Coming Soon
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All Plugins Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredPlugins.map((plugin) => (
            <div key={plugin.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{plugin.icon}</span>
                    <div>
                      <h3 className="text-lg font-semibold text-text-primary">{plugin.name}</h3>
                      <p className="text-sm text-text-secondary">{plugin.description}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(plugin.status)}
                    {getPriceBadge(plugin.price)}
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className="text-yellow-400">⭐</span>
                    <span className="text-sm text-text-secondary">{plugin.rating}</span>
                    <span className="text-sm text-text-secondary">({plugin.installs})</span>
                  </div>
                </div>

                {/* Features */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {plugin.features.slice(0, 2).map((feature, index) => (
                      <span key={index} className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                        {feature}
                      </span>
                    ))}
                    {plugin.features.length > 2 && (
                      <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded">
                        +{plugin.features.length - 2} more
                      </span>
                    )}
                  </div>
                </div>

                {/* Action Button */}
                {plugin.status === 'active' ? (
                  <button
                    onClick={() => handlePluginToggle(plugin.id)}
                    className="w-full bg-red-100 text-red-800 py-2 px-4 rounded-lg font-medium hover:bg-red-200 transition-colors"
                  >
                    Deactivate
                  </button>
                ) : plugin.status === 'inactive' ? (
                  <button
                    onClick={() => handlePluginToggle(plugin.id)}
                    className="w-full bg-green-100 text-green-800 py-2 px-4 rounded-lg font-medium hover:bg-green-200 transition-colors"
                  >
                    Activate
                  </button>
                ) : (
                  <button
                    disabled
                    className="w-full bg-gray-100 text-gray-400 py-2 px-4 rounded-lg font-medium cursor-not-allowed"
                  >
                    Coming Soon
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredPlugins.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-text-primary mb-2">No plugins found</h3>
            <p className="text-text-secondary">Try adjusting your search or filter criteria</p>
          </div>
        )}

        {/* Plugin Change Notification */}
        {showNotification && (
          <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 ease-in-out ${
            notificationType === 'success'
              ? 'bg-green-500 text-white'
              : 'bg-blue-500 text-white'
          } animate-menu-item-bounce`}>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="font-medium">{notificationMessage}</span>
            </div>
          </div>
        )}
        {/* Example usage buttons for navigate and showPluginNotification */}
        <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
          <button
            onClick={() => navigate('/')}
            className="bg-blue-100 text-blue-800 py-2 px-4 rounded-lg font-medium hover:bg-blue-200 transition-colors"
          >
          Go Home (navigate)
          </button>
          <button
            onClick={() => showPluginNotification('This is a test notification!', 'info')}
            className="bg-green-100 text-green-800 py-2 px-4 rounded-lg font-medium hover:bg-green-200 transition-colors"
          >
          Show Notification
          </button>
        </div>
      </div>
    </div>
  );
};

export default PluginStorePage;
