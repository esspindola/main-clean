import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, Plus, X } from 'lucide-react';
import { productsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface VariantValue {
  id: string;
  value: string;
  selected: boolean;
}

interface VariantData {
  [key: string]: {
    isActive: boolean;
    values: VariantValue[];
    newValue: string;
    showPanel: boolean;
  };
}

const NewProductPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    productType: 'Physical Product',
    name: '',
    description: '',
    location: '',
    createCategory: false,
    unit: 'Per item',
    weight: '',
    price: '',
    inventoryQuantity: '',
    lowStockAlert: '',
    sku: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);

  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [showMoreVariantsPanel, setShowMoreVariantsPanel] = useState(false);

  const existingCategories = [
    'Furniture',
    'Textiles', 
    'Lighting',
    'Electronics',
    'Decoration',
    'Office'
  ];

  const variantTypes = [
    'Color',
    'Size',
    'Material',
    'Style',
    'Finish'
  ];

  const [variants, setVariants] = useState<VariantData>({
    Color: {
      isActive: false,
      values: [
        { id: '1', value: 'Red', selected: false },
        { id: '2', value: 'Blue', selected: false },
        { id: '3', value: 'Green', selected: false },
        { id: '4', value: 'Black', selected: false }
      ],
      newValue: '',
      showPanel: false
    },
    Size: {
      isActive: false,
      values: [
        { id: '1', value: 'Small', selected: false },
        { id: '2', value: 'Medium', selected: false },
        { id: '3', value: 'Large', selected: false },
        { id: '4', value: 'Extra Large', selected: false }
      ],
      newValue: '',
      showPanel: false
    },
    Material: {
      isActive: false,
      values: [
        { id: '1', value: 'Wood', selected: false },
        { id: '2', value: 'Metal', selected: false },
        { id: '3', value: 'Plastic', selected: false },
        { id: '4', value: 'Glass', selected: false }
      ],
      newValue: '',
      showPanel: false
    },
    Style: {
      isActive: false,
      values: [
        { id: '1', value: 'Modern', selected: false },
        { id: '2', value: 'Classic', selected: false },
        { id: '3', value: 'Minimalist', selected: false },
        { id: '4', value: 'Industrial', selected: false }
      ],
      newValue: '',
      showPanel: false
    },
    Finish: {
      isActive: false,
      values: [
        { id: '1', value: 'Matte', selected: false },
        { id: '2', value: 'Glossy', selected: false },
        { id: '3', value: 'Satin', selected: false },
        { id: '4', value: 'Textured', selected: false }
      ],
      newValue: '',
      showPanel: false
    }
  });

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // File upload handlers
  const handleFileSelect = (files: FileList | null) => {
    if (files) {
      const fileArray = Array.from(files);
      const validFiles = fileArray.filter(file => 
        file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024 // 5MB limit
      );
      
      if (validFiles.length !== fileArray.length) {
        setError('Some files were rejected. Only images under 5MB are allowed.');
        setTimeout(() => setError(null), 5000);
      }
      
      setSelectedFiles(prev => [...prev, ...validFiles]);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleCategoryToggle = (category: string) => {
    setSelectedCategories(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const handleVariantToggle = (variantType: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        isActive: !prev[variantType].isActive,
        showPanel: !prev[variantType].isActive ? true : false
      }
    }));
  };

  const handleVariantValueToggle = (variantType: string, valueId: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        values: prev[variantType].values.map(value =>
          value.id === valueId ? { ...value, selected: !value.selected } : value
        )
      }
    }));
  };

  const handleAddVariantValue = (variantType: string) => {
    const newValue = variants[variantType].newValue.trim();
    if (newValue) {
      const newId = Date.now().toString();
      setVariants(prev => ({
        ...prev,
        [variantType]: {
          ...prev[variantType],
          values: [...prev[variantType].values, { id: newId, value: newValue, selected: true }],
          newValue: ''
        }
      }));
    }
  };

  const handleNewValueChange = (variantType: string, value: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        newValue: value
      }
    }));
  };

  const handleSaveVariant = (variantType: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        showPanel: false
      }
    }));
  };

  const handleCancelVariant = (variantType: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        showPanel: false,
        isActive: false,
        values: prev[variantType].values.map(value => ({ ...value, selected: false })),
        newValue: ''
      }
    }));
  };

  const getSelectedValues = (variantType: string) => {
    return variants[variantType].values
      .filter(value => value.selected)
      .map(value => value.value)
      .join(', ');
  };

  const handleMoreVariantsToggle = (variantType: string) => {
    setVariants(prev => ({
      ...prev,
      [variantType]: {
        ...prev[variantType],
        isActive: !prev[variantType].isActive
      }
    }));
  };

  const handleSaveMoreVariants = () => {
    setShowMoreVariantsPanel(false);
  };

  const handleSave = async () => {
    console.log('handleSave called');
    
    if (!isAuthenticated) {
      console.log('User not authenticated');
      setError('You must log in to create products');
      return;
    }

    if (!formData.name || !formData.price) {
      console.log('Missing required fields:', { name: formData.name, price: formData.price });
      setError('Name and price are required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      console.log('Creating FormData...');
      console.log('Selected files:', selectedFiles);

      // Create FormData for multipart/form-data request
      const formDataToSend = new FormData();
      formDataToSend.append('name', formData.name);
      formDataToSend.append('description', formData.description);
      formDataToSend.append('price', formData.price);
      formDataToSend.append('stock', (parseInt(formData.inventoryQuantity) || 0).toString());
      formDataToSend.append('category', selectedCategories[0] || 'General');
      if (formData.sku) {
        formDataToSend.append('sku', formData.sku);
      }

      // Add images to FormData
      selectedFiles.forEach((file) => {
        console.log('Adding file to FormData:', file.name);
        formDataToSend.append('images', file);
      });

      const token = localStorage.getItem('token');
      console.log('Token:', token);
      console.log('Sending request to:', 'http://localhost:4444/api/products');

      const response = await fetch('http://localhost:4444/api/products', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formDataToSend
      });

      console.log('Response status:', response.status);
      const result = await response.json();
      console.log('Response result:', result);
      
      if (result.success) {
        console.log('Product created successfully:', result.product);
        navigate('/inventory');
      } else {
        console.log('Error creating product:', result.message);
        setError(result.message || 'Error creating product');
      }
    } catch (err) {
      console.error('Error creating product:', err);
      setError('Error creating product');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-main pt-16">
      {/* Sub-header */}
      <div className="bg-bg-surface shadow-sm border-b border-divider">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => navigate('/inventory')}
                className="p-2 hover:bg-gray-50 rounded-full transition-colors md:hidden"
              >
                <ArrowLeft size={20} className="text-text-primary" />
              </button>
              <h1 className="text-xl font-semibold text-text-primary md:hidden">New Product</h1>
            </div>
            
            <div className="flex items-center space-x-3">
              {error && (
                <div className="text-red-500 text-sm">
                  {error}
                </div>
              )}
              <button 
                onClick={handleSave}
                disabled={loading}
                className={`bg-primary hover:bg-primary-600 text-black font-medium px-6 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <span>Save</span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* Desktop Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Left Column */}
          <div className="space-y-6">
            
            {/* Product Type */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Product Type
                  </label>
                  <select
                    value={formData.productType}
                    onChange={(e) => handleInputChange('productType', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                  >
                    <option value="Physical Product">Physical Product</option>
                    <option value="Service">Service</option>
                    <option value="Digital">Digital</option>
                  </select>
                </div>
                <button className="ml-4 px-4 py-2 text-sm border border-divider rounded-lg hover:bg-gray-50 transition-colors text-text-primary">
                  Change
                </button>
              </div>
            </div>

            {/* Basic Information */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Product Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      placeholder="Product name"
                      className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-text-primary mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      placeholder="Product description"
                      rows={3}
                      className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary resize-none"
                    />
                  </div>
            </div>

            {/* Image Upload */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <label className="block text-sm font-medium text-text-primary mb-4">
                Product Images
              </label>
              <div 
                className={`border-2 border-dashed border-divider rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer ${
                  dragActive ? 'border-complement' : ''
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <input
                  type="file"
                  multiple
                  accept="image/*"
                  onChange={(e) => handleFileSelect(e.target.files)}
                  className="hidden"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="cursor-pointer">
                  <Upload size={48} className="text-text-secondary mx-auto mb-4" />
                  <p className="text-text-secondary mb-2">Drag and drop images here</p>
                  <p className="text-sm text-text-secondary">or click to select files</p>
                </label>
              </div>
              {selectedFiles.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center bg-gray-100 text-gray-800 text-sm rounded-md p-2">
                      <span>{file.name}</span>
                      <button
                        onClick={() => removeFile(index)}
                        className="ml-2 text-gray-500 hover:text-gray-700"
                      >
                        <X size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Location */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <label className="block text-sm font-medium text-text-primary mb-2">
                Locations
              </label>
              <select
                value={formData.location}
                onChange={(e) => handleInputChange('location', e.target.value)}
                className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              >
                <option value="">Select a warehouse</option>
                <option value="almacen-principal">Main Warehouse</option>
                <option value="almacen-secundario">Secondary Warehouse</option>
                <option value="tienda-fisica">Physical Store</option>
              </select>
            </div>

            {/* Categorization */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <h3 className="text-lg font-medium text-text-primary mb-4">Categorization</h3>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="create-category"
                    checked={formData.createCategory}
                    onChange={(e) => handleInputChange('createCategory', e.target.checked)}
                    className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                  />
                  <label htmlFor="create-category" className="text-sm font-medium text-text-primary">
                    Create category
                  </label>
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-3">
                    Existing categories
                  </label>
                  <div className="space-y-2">
                    {existingCategories.map((category) => (
                      <div key={category} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={`category-${category}`}
                          checked={selectedCategories.includes(category)}
                          onChange={() => handleCategoryToggle(category)}
                          className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                        />
                        <label htmlFor={`category-${category}`} className="text-sm text-text-primary">
                          {category}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            
            {/* Units Section */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <h3 className="text-lg font-medium text-text-primary mb-4">Units</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Unit
                  </label>
                  <select
                    value={formData.unit}
                    onChange={(e) => handleInputChange('unit', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                  >
                    <option value="Per item">Per item</option>
                    <option value="Per kilogramo">Per kilogramo</option>
                    <option value="Per metro">Per metro</option>
                    <option value="Per litro">Per litro</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Weight (kg)
                  </label>
                  <input
                    type="number"
                    value={formData.weight}
                    onChange={(e) => handleInputChange('weight', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                    placeholder="0.00"
                    step="0.01"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Price (required)
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary">$</span>
                    <input
                      type="number"
                      value={formData.price}
                      onChange={(e) => handleInputChange('price', e.target.value)}
                      className="w-full pl-8 pr-3 py-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                      placeholder="0.00"
                      step="0.01"
                    />
                  </div>
                </div>

                <button className="w-full p-3 border border-dashed border-divider rounded-lg text-text-secondary hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                  <Plus size={16} />
                  <span>Add additional unit</span>
                </button>
              </div>
            </div>

            {/* Inventory Section */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <h3 className="text-lg font-medium text-text-primary mb-4">Inventory</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Inventory quantity
                  </label>
                  <input
                    type="number"
                    value={formData.inventoryQuantity}
                    onChange={(e) => handleInputChange('inventoryQuantity', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Low stock alert
                  </label>
                  <input
                    type="number"
                    value={formData.lowStockAlert}
                    onChange={(e) => handleInputChange('lowStockAlert', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                    placeholder="5"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    SKU
                  </label>
                  <input
                    type="text"
                    value={formData.sku}
                    onChange={(e) => handleInputChange('sku', e.target.value)}
                    className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                    placeholder="SKU-001"
                  />
                </div>
              </div>
            </div>

            {/* Variants Section */}
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
              <h3 className="text-lg font-medium text-text-primary mb-4">Variants</h3>
              
              <div className="space-y-4">
                {variantTypes.map((variant) => (
                  <div key={variant} className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`variant-${variant}`}
                        checked={variants[variant].isActive}
                        onChange={() => handleVariantToggle(variant)}
                        className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                      />
                      <label htmlFor={`variant-${variant}`} className="text-sm text-text-primary">
                        {variant}
                      </label>
                    </div>

                    {/* Show selected values summary */}
                    {variants[variant].isActive && !variants[variant].showPanel && getSelectedValues(variant) && (
                      <div className="ml-6 text-sm text-text-secondary">
                        {variant}: {getSelectedValues(variant)}
                      </div>
                    )}

                    {/* Inline Panel */}
                    {variants[variant].showPanel && (
                      <div className="ml-6 border border-divider rounded-lg p-4 bg-gray-50">
                        <div className="flex items-center justify-between mb-3">
                          <h4 className="font-medium text-text-primary">{variant}</h4>
                          <button
                            onClick={() => handleCancelVariant(variant)}
                            className="p-1 hover:bg-gray-200 rounded transition-colors"
                          >
                            <X size={16} className="text-text-secondary" />
                          </button>
                        </div>

                        {/* Add new value */}
                        <div className="flex items-center space-x-2 mb-3">
                          <input
                            type="text"
                            value={variants[variant].newValue}
                            onChange={(e) => handleNewValueChange(variant, e.target.value)}
                            placeholder="Add value"
                            className="flex-1 p-2 border border-divider rounded text-sm focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                          />
                          <button
                            onClick={() => handleAddVariantValue(variant)}
                            className="p-2 bg-complement hover:bg-complement-600 text-white rounded transition-colors"
                          >
                            <Plus size={16} />
                          </button>
                        </div>

                        {/* Existing values */}
                        <div className="space-y-2 mb-4">
                          {variants[variant].values.map((value) => (
                            <div key={value.id} className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                id={`${variant}-${value.id}`}
                                checked={value.selected}
                                onChange={() => handleVariantValueToggle(variant, value.id)}
                                className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                              />
                              <label htmlFor={`${variant}-${value.id}`} className="text-sm text-text-primary">
                                {value.value}
                              </label>
                            </div>
                          ))}
                        </div>

                        {/* Panel actions */}
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleSaveVariant(variant)}
                            className="px-3 py-1 bg-success hover:bg-success-600 text-white text-sm rounded transition-colors"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => handleCancelVariant(variant)}
                            className="px-3 py-1 bg-gray-300 hover:bg-gray-400 text-text-primary text-sm rounded transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                <button 
                  onClick={() => setShowMoreVariantsPanel(true)}
                  className="w-full p-3 border border-dashed border-divider rounded-lg text-text-secondary hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2 mt-4"
                >
                  <Plus size={16} />
                  <span>Add more variants</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* More Variants Floating Panel */}
      {showMoreVariantsPanel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-60 flex items-center justify-center p-4">
          <div className="bg-bg-surface rounded-lg shadow-xl max-w-md w-full p-6 border border-divider">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-text-primary">Add Variants</h3>
              <button
                onClick={() => setShowMoreVariantsPanel(false)}
                className="p-1 hover:bg-gray-50 rounded transition-colors"
              >
                <X size={20} className="text-text-secondary" />
              </button>
            </div>

            <div className="space-y-3 mb-6">
              {variantTypes.map((variant) => (
                <div key={variant} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`more-variant-${variant}`}
                    checked={variants[variant].isActive}
                    onChange={() => handleMoreVariantsToggle(variant)}
                    className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                  />
                  <label htmlFor={`more-variant-${variant}`} className="text-sm text-text-primary">
                    {variant}
                  </label>
                </div>
              ))}
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleSaveMoreVariants}
                className="flex-1 bg-success hover:bg-success-600 text-white font-medium py-2 rounded-lg transition-colors"
              >
                Save
              </button>
              <button
                onClick={() => setShowMoreVariantsPanel(false)}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-text-primary font-medium py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewProductPage;