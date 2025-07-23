import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { productsAPI } from '../services/api';

const OCRResultPage: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedResult, setEditedResult] = useState<any>(null);
  const [isAddingToInventory, setIsAddingToInventory] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('Office Supplies');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError('');
    }
  };

  const handleProcessAnother = () => {
    setFile(null);
    setResult(null);
    setError('');
    setIsEditing(false);
    setEditedResult(null);
    // Clear file input
    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleConfirmData = async () => {
    if (!result || !token) {
      setError('No data to confirm or not authenticated');
      return;
    }

    setIsAddingToInventory(true);
    setError('');

    try {
      // Add each detected item to inventory
      const productsToAdd = result.items.map((item: any) => ({
        name: item.name,
        description: item.description,
        price: item.unitPrice,
        stock: item.quantity,
        category: selectedCategory,
        status: 'active'
      }));

      const addedProducts = [];
      const failedProducts = [];
      
      for (const productData of productsToAdd) {
        try {
          const response = await productsAPI.create(productData);
          addedProducts.push(response.product);
        } catch (error: any) {
          console.error('Error adding product:', productData.name, error);
          failedProducts.push({
            name: productData.name,
            error: error.message || 'Unknown error'
          });
          // Continue with other products even if one fails
        }
      }

      if (addedProducts.length > 0) {
        // Show success message and navigate to inventory
        let message = `Successfully added ${addedProducts.length} products to inventory!`;
        if (failedProducts.length > 0) {
          message += `\n\nFailed to add ${failedProducts.length} products:`;
          failedProducts.forEach(product => {
            message += `\n- ${product.name}: ${product.error}`;
          });
        }
        alert(message);
        navigate('/inventory');
      } else {
        setError('Failed to add any products to inventory');
      }
    } catch (error) {
      console.error('Error adding products to inventory:', error);
      setError('Failed to add products to inventory. Please try again.');
    } finally {
      setIsAddingToInventory(false);
    }
  };

  const handleEditResult = () => {
    setIsEditing(true);
    setEditedResult(JSON.parse(JSON.stringify(result))); // Deep copy
  };

  const handleSaveEdit = () => {
    setResult(editedResult);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedResult(null);
  };

  const handleItemChange = (index: number, field: string, value: any) => {
    if (!editedResult) return;
    
    const newItems = [...editedResult.items];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Recalculate item total
    if (field === 'quantity' || field === 'unitPrice') {
      newItems[index].total = newItems[index].quantity * newItems[index].unitPrice;
    }
    
    // Recalculate totals
    const subtotal = newItems.reduce((sum, item) => sum + item.total, 0);
    const taxes = subtotal * 0.15; // 15% taxes
    const total = subtotal + taxes;
    
    setEditedResult({
      ...editedResult,
      items: newItems,
      subtotal,
      taxes,
      total
    });
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulated automatic result
    const mockResult = {
      documentType: 'invoice',
      supplier: 'Supplier ABC Inc.',
      date: '2024-01-15',
      invoiceNumber: 'INV-2024-001',
      total: 1250.00,
      items: [
        {
          name: 'Cabinet with Doors',
          description: 'Wooden cabinet with sliding doors',
          quantity: 5,
          unitPrice: 180.00,
          total: 900.00
        },
        {
          name: 'Executive Desk',
          description: 'Premium office desk',
          quantity: 2,
          unitPrice: 250.00,
          total: 500.00
        }
      ],
      subtotal: 1062.50,
      taxes: 187.50,
      confidence: 0.95,
      file: file.name
    };
    
    setResult(mockResult);
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        {!result ? (
          // File selection form
          <div className="bg-white rounded-lg shadow-lg p-6 md:p-8 animate-fadeIn">
            <div className="text-center mb-6 md:mb-8">
              <div className="text-3xl md:text-4xl mb-4">🔍</div>
              <h2 className="text-2xl md:text-3xl font-bold text-text-primary mb-2">Process Document with OCR</h2>
              <p className="text-text-secondary text-sm md:text-base">Upload a document to extract information automatically</p>
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-text-primary mb-3">
                📁 Select document
              </label>
              <div className="border-2 border-dashed border-divider rounded-lg p-6 md:p-8 text-center hover:border-complement transition-colors duration-300">
      <input
        type="file"
        accept=".pdf,image/*"
        onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <div className="text-text-secondary">
                    <div className="text-4xl md:text-5xl mb-4 animate-bounce">📄</div>
                    <p className="text-base md:text-lg font-medium">
                      {file ? `Selected file: ${file.name}` : 'Click to select a file'}
                    </p>
                    <p className="text-xs md:text-sm text-text-secondary mt-2">
                      PDF, JPG, PNG, GIF (max 10MB)
                    </p>
                  </div>
                </label>
              </div>
            </div>
            
            <div className="text-center">
      <button
        onClick={handleUpload}
        disabled={!file || loading}
                className="bg-complement text-white px-6 md:px-8 py-3 md:py-4 rounded-lg font-medium hover:bg-complement-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 flex items-center mx-auto"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 md:h-5 w-4 md:w-5 border-b-2 border-white mr-2 md:mr-3"></div>
                    Processing document...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔍</span>
                    Upload and process
                  </>
                )}
              </button>
            </div>
            
            {error && (
              <div className="mt-4 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700 animate-shake">
                {error}
              </div>
            )}
          </div>
        ) : (
          // Processing result
          <div className="bg-white rounded-lg shadow-lg p-6 md:p-8 animate-fadeIn">
            <div className="text-center mb-6 md:mb-8">
              <div className="text-3xl md:text-4xl mb-4">📄</div>
              <h2 className="text-xl md:text-2xl font-bold text-text-primary mb-2">OCR Processing Result</h2>
              <p className="text-text-secondary text-sm md:text-base">Document processed successfully</p>
              <div className="mt-4 inline-block bg-green-50 border border-green-200 rounded-lg px-4 py-2">
                <div className="text-sm text-text-secondary">Confidence</div>
                <div className="text-lg font-bold text-green-600">{(result.confidence * 100).toFixed(1)}%</div>
              </div>
            </div>
            
            {/* Document information */}
            <div className="grid md:grid-cols-2 gap-6 md:gap-8 mb-6 md:mb-8">
              <div className="bg-bg-surface rounded-lg p-4 md:p-6">
                <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">📋 Document Information</h3>
                <div className="space-y-2 md:space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Type:</span>
                    <span className="text-text-primary capitalize text-sm md:text-base">{result.documentType}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Supplier:</span>
                    <span className="text-text-primary text-sm md:text-base">{result.supplier}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Date:</span>
                    <span className="text-text-primary text-sm md:text-base">{result.date}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Number:</span>
                    <span className="text-text-primary text-sm md:text-base">{result.invoiceNumber}</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-bg-surface rounded-lg p-4 md:p-6">
                <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">💰 Financial Summary</h3>
                <div className="space-y-2 md:space-y-3">
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Subtotal:</span>
                    <span className="text-text-primary text-sm md:text-base">${result.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium text-text-secondary text-sm md:text-base">Taxes:</span>
                    <span className="text-text-primary text-sm md:text-base">${result.taxes.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between border-t border-divider pt-2">
                    <span className="font-bold text-text-primary text-sm md:text-base">Total:</span>
                    <span className="text-lg md:text-xl font-bold text-green-600">${result.total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Items table */}
            <div className="mb-6 md:mb-8">
              <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">📦 Detected Items</h3>
              <div className="bg-bg-surface rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead>
                      <tr className="bg-divider">
                        <th className="px-3 md:px-6 py-3 md:py-4 text-left text-xs md:text-sm font-medium text-text-primary">Name</th>
                        <th className="px-3 md:px-6 py-3 md:py-4 text-left text-xs md:text-sm font-medium text-text-primary">Description</th>
                        <th className="px-3 md:px-6 py-3 md:py-4 text-right text-xs md:text-sm font-medium text-text-primary">Quantity</th>
                        <th className="px-3 md:px-6 py-3 md:py-4 text-right text-xs md:text-sm font-medium text-text-primary">Unit Price</th>
                        <th className="px-3 md:px-6 py-3 md:py-4 text-right text-xs md:text-sm font-medium text-text-primary">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(isEditing ? editedResult : result).items.map((item: any, index: number) => (
                        <tr key={index} className="border-b border-divider hover:bg-gray-50 transition-colors">
                          <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-text-primary">
                            {isEditing ? (
                              <input
                                type="text"
                                value={item.name}
                                onChange={(e) => handleItemChange(index, 'name', e.target.value)}
                                className="w-full px-2 md:px-3 py-1 md:py-2 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent text-xs md:text-sm"
                              />
                            ) : (
                              item.name
                            )}
                          </td>
                          <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-text-primary">
                            {isEditing ? (
                              <input
                                type="text"
                                value={item.description}
                                onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                                className="w-full px-2 md:px-3 py-1 md:py-2 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent text-xs md:text-sm"
                              />
                            ) : (
                              item.description
                            )}
                          </td>
                          <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-text-primary text-right">
                            {isEditing ? (
                              <input
                                type="number"
                                value={item.quantity}
                                onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 0)}
                                className="w-16 md:w-20 px-2 md:px-3 py-1 md:py-2 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent text-right text-xs md:text-sm"
                              />
                            ) : (
                              item.quantity
                            )}
                          </td>
                          <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm text-text-primary text-right">
                            {isEditing ? (
                              <input
                                type="number"
                                step="0.01"
                                value={item.unitPrice}
                                onChange={(e) => handleItemChange(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                                className="w-20 md:w-24 px-2 md:px-3 py-1 md:py-2 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent text-right text-xs md:text-sm"
                              />
                            ) : (
                              `$${item.unitPrice.toFixed(2)}`
                            )}
                          </td>
                          <td className="px-3 md:px-6 py-3 md:py-4 text-xs md:text-sm font-medium text-text-primary text-right">
                            ${item.total.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* File information */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 md:p-4 mb-6 md:mb-8">
              <div className="flex items-center">
                <span className="text-blue-600 mr-2 md:mr-3">📁</span>
                <span className="text-xs md:text-sm text-blue-800">
                  <strong>Processed file:</strong> {result.file}
                </span>
              </div>
            </div>

            {/* Category selection */}
            <div className="mb-6 md:mb-8">
              <h3 className="text-base md:text-lg font-semibold text-text-primary mb-3 md:mb-4">📂 Product Category</h3>
              <div className="bg-bg-surface rounded-lg p-4 md:p-6">
                <label className="block text-sm font-medium text-text-primary mb-2">
                  Select category for all products:
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-white text-text-primary"
                >
                  <option value="Office Supplies">Office Supplies</option>
                  <option value="Electronics">Electronics</option>
                  <option value="Furniture">Furniture</option>
                  <option value="Clothing">Clothing</option>
                  <option value="Food & Beverages">Food & Beverages</option>
                  <option value="Books">Books</option>
                  <option value="Sports">Sports</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="mb-6 md:mb-8 p-4 bg-error-50 border border-error-200 rounded-lg text-error-700 animate-shake">
                <div className="flex items-center">
                  <span className="text-error-600 mr-2">⚠️</span>
                  <span className="text-sm">{error}</span>
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center">
              {isEditing ? (
                <>
                  <button 
                    onClick={handleSaveEdit}
                    className="bg-green-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-lg font-medium hover:bg-green-700 transition-all duration-300 transform hover:scale-105 text-sm md:text-base"
                  >
                    💾 Save Changes
                  </button>
                  <button 
                    onClick={handleCancelEdit}
                    className="bg-gray-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-lg font-medium hover:bg-gray-700 transition-all duration-300 transform hover:scale-105 text-sm md:text-base"
                  >
                    ❌ Cancel
                  </button>
                </>
              ) : (
                <>
                  <button 
                    onClick={handleConfirmData}
                    disabled={isAddingToInventory}
                    className="bg-green-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105 text-sm md:text-base"
                  >
                    {isAddingToInventory ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2 inline-block"></div>
                        Adding to Inventory...
                      </>
                    ) : (
                      '✅ Confirm Data'
                    )}
                  </button>
                  <button 
                    onClick={handleEditResult}
                    className="bg-blue-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-lg font-medium hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 text-sm md:text-base"
                  >
                    📝 Edit Result
                  </button>
                  <button 
                    onClick={handleProcessAnother}
                    className="bg-gray-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-lg font-medium hover:bg-gray-700 transition-all duration-300 transform hover:scale-105 text-sm md:text-base"
                  >
                    🔄 Process Another
      </button>
                </>
              )}
            </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default OCRResultPage; 