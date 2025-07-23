import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Brain, Archive, ArrowRight } from 'lucide-react';

const SmartInventoryPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center mb-6">
          <Brain className="w-8 h-8 text-complement mr-3" />
          <h1 className="text-3xl font-bold text-text-primary">Smart Inventory</h1>
        </div>
        
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-text-primary mb-4">
            🚀 Feature in Development
          </h2>
          <p className="text-text-secondary mb-4">
            Smart Inventory with AI is being developed. This feature will include:
          </p>
          <ul className="space-y-2 text-text-secondary mb-6">
            <li className="flex items-center">
              <span className="w-2 h-2 bg-complement rounded-full mr-3"></span>
              Predictive inventory analysis
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-complement rounded-full mr-3"></span>
              Automatic detection of low stock products
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-complement rounded-full mr-3"></span>
              Restocking recommendations
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 bg-complement rounded-full mr-3"></span>
              Sales trend analysis
            </li>
          </ul>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white border border-divider rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <Archive className="w-6 h-6 text-complement mr-3" />
              <h3 className="text-lg font-semibold text-text-primary">Current Inventory</h3>
            </div>
            <p className="text-text-secondary mb-4">
              Access the traditional inventory with all available features.
            </p>
            <button
              onClick={() => navigate('/inventory')}
              className="flex items-center text-complement hover:text-complement-700 font-medium"
            >
              Go to Inventory
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>

          <div className="bg-white border border-divider rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center mb-4">
              <Brain className="w-6 h-6 text-purple-600 mr-3" />
              <h3 className="text-lg font-semibold text-text-primary">OCR Documents</h3>
            </div>
            <p className="text-text-secondary mb-4">
              Process documents with OCR to extract information automatically.
            </p>
            <button
              onClick={() => navigate('/ocr-result')}
              className="flex items-center text-purple-600 hover:text-purple-700 font-medium"
            >
              Process Documents
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>

        <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 className="font-semibold text-yellow-800 mb-2">💡 Coming Soon</h4>
          <p className="text-yellow-700 text-sm">
            We are working on integrating artificial intelligence to make your inventory smarter. 
            Meanwhile, you can use all the features of the traditional inventory.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SmartInventoryPage; 