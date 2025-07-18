import React, { useState, useEffect } from 'react';
import { ArrowLeft, CreditCard, Smartphone, Bitcoin, Banknote, Calculator } from 'lucide-react';

interface PaymentScreenProps {
  isOpen: boolean;
  onBack: () => void;
  onPaymentSuccess: (method: string) => void;
  total: number;
}

type PaymentMethod = 'card' | 'wallet' | 'crypto' | 'cash';

const PaymentScreen: React.FC<PaymentScreenProps> = ({ isOpen, onBack, onPaymentSuccess, total }) => {
  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod | null>(null);
  const [formData, setFormData] = useState({
    cardNumber: '',
    expiryDate: '',
    cvc: '',
    cardName: '',
    cryptoCurrency: 'bitcoin',
    walletAddress: '',
    cashAmount: total.toString(),
    needsChange: false,
    changeFor: ''
  });

  // Estados para el cálculo de cambio
  const [cashReceived, setCashReceived] = useState<number>(0);
  const [changeAmount, setChangeAmount] = useState<number>(0);
  const [isSufficientAmount, setIsSufficientAmount] = useState<boolean>(false);

  // Calcular cambio automáticamente cuando cambia el monto recibido
  useEffect(() => {
    const received = parseFloat(cashReceived.toString()) || 0;
    const change = received - total;
    setChangeAmount(change);
    setIsSufficientAmount(received >= total);
  }, [cashReceived, total]);

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCashReceivedChange = (value: string) => {
    const amount = parseFloat(value) || 0;
    setCashReceived(amount);
  };

  const isFormValid = () => {
    switch (selectedMethod) {
      case 'card':
        return formData.cardNumber && formData.expiryDate && formData.cvc && formData.cardName;
      case 'wallet':
        return true; // Wallet payments are handled externally
      case 'crypto':
        return formData.walletAddress;
      case 'cash':
        return cashReceived >= total; // Debe recibir al menos el total
      default:
        return false;
    }
  };

  const getPaymentMethodName = (method: PaymentMethod | null) => {
    switch (method) {
      case 'card':
        return 'Tarjeta de Crédito/Débito';
      case 'wallet':
        return 'Apple Pay / Google Pay';
      case 'crypto':
        return 'Coinbase Pay / Crypto';
      case 'cash':
        return 'Cash on Delivery';
      default:
        return 'Método de pago';
    }
  };

  const handleConfirmPayment = () => {
    if (isFormValid() && selectedMethod) {
      onPaymentSuccess(getPaymentMethodName(selectedMethod));
    }
  };

  // Función para formatear moneda
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-bg-main z-50 flex flex-col animate-scale-in">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-divider bg-bg-surface">
        <button 
          onClick={onBack}
          className="p-2 hover:bg-gray-50 rounded-full transition-all duration-300 hover:scale-110 icon-bounce"
        >
          <ArrowLeft size={20} className="text-text-primary" />
        </button>
        <h1 className="text-lg font-semibold text-text-primary animate-slide-in-left">Opciones de Pago</h1>
        <div className="w-10"></div> {/* Spacer */}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 pb-24">
        {/* Total Amount */}
        <div className="bg-gray-50 p-4 rounded-lg mb-6 border border-divider animate-bounce-in">
          <div className="text-center">
            <span className="text-sm text-text-secondary">Total a pagar</span>
            <div className="text-2xl font-bold text-text-primary">{formatCurrency(total)}</div>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="space-y-4 mb-6 animate-stagger">
          {/* Credit/Debit Card */}
          <div 
            className={`border rounded-lg p-4 cursor-pointer transition-all duration-300 hover-lift ${
              selectedMethod === 'card' ? 'border-complement bg-complement-50 shadow-lg' : 'border-divider hover:border-gray-300 bg-bg-surface'
            }`}
            onClick={() => setSelectedMethod('card')}
          >
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${
                selectedMethod === 'card' ? 'border-complement bg-complement' : 'border-gray-300'
              }`}>
                {selectedMethod === 'card' && <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5 animate-scale-in"></div>}
              </div>
              <CreditCard size={20} className="text-text-secondary icon-bounce" />
              <div>
                <div className="font-medium text-text-primary text-glow">Tarjeta de Crédito/Débito</div>
                <div className="text-sm text-text-secondary">Visa, Mastercard, American Express</div>
              </div>
            </div>
          </div>

          {/* Apple Pay / Google Pay */}
          <div 
            className={`border rounded-lg p-4 cursor-pointer transition-all duration-300 hover-lift ${
              selectedMethod === 'wallet' ? 'border-complement bg-complement-50 shadow-lg' : 'border-divider hover:border-gray-300 bg-bg-surface'
            }`}
            onClick={() => setSelectedMethod('wallet')}
          >
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${
                selectedMethod === 'wallet' ? 'border-complement bg-complement' : 'border-gray-300'
              }`}>
                {selectedMethod === 'wallet' && <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5 animate-scale-in"></div>}
              </div>
              <Smartphone size={20} className="text-text-secondary icon-bounce" />
              <div>
                <div className="font-medium text-text-primary text-glow">Apple Pay / Google Pay</div>
                <div className="text-sm text-text-secondary">Pago rápido con tu wallet</div>
              </div>
            </div>
          </div>

          {/* Crypto */}
          <div 
            className={`border rounded-lg p-4 cursor-pointer transition-all duration-300 hover-lift ${
              selectedMethod === 'crypto' ? 'border-complement bg-complement-50 shadow-lg' : 'border-divider hover:border-gray-300 bg-bg-surface'
            }`}
            onClick={() => setSelectedMethod('crypto')}
          >
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${
                selectedMethod === 'crypto' ? 'border-complement bg-complement' : 'border-gray-300'
              }`}>
                {selectedMethod === 'crypto' && <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5 animate-scale-in"></div>}
              </div>
              <Bitcoin size={20} className="text-text-secondary icon-bounce" />
              <div>
                <div className="font-medium text-text-primary text-glow">Coinbase Pay / Crypto</div>
                <div className="text-sm text-text-secondary">Bitcoin, Ethereum, y más</div>
              </div>
            </div>
          </div>

          {/* Cash on Delivery */}
          <div 
            className={`border rounded-lg p-4 cursor-pointer transition-all duration-300 hover-lift ${
              selectedMethod === 'cash' ? 'border-complement bg-complement-50 shadow-lg' : 'border-divider hover:border-gray-300 bg-bg-surface'
            }`}
            onClick={() => setSelectedMethod('cash')}
          >
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${
                selectedMethod === 'cash' ? 'border-complement bg-complement' : 'border-gray-300'
              }`}>
                {selectedMethod === 'cash' && <div className="w-2 h-2 bg-white rounded-full mx-auto mt-0.5 animate-scale-in"></div>}
              </div>
              <Banknote size={20} className="text-text-secondary icon-bounce" />
              <div>
                <div className="font-medium text-text-primary text-glow">Cash on Delivery</div>
                <div className="text-sm text-text-secondary">Pago en efectivo al recibir</div>
              </div>
            </div>
          </div>
        </div>

        {/* Payment Forms */}
        {selectedMethod === 'card' && (
          <div className="space-y-4">
            <h3 className="font-medium text-text-primary">Información de la Tarjeta</h3>
            
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Número de tarjeta
              </label>
              <input
                type="text"
                value={formData.cardNumber}
                onChange={(e) => handleInputChange('cardNumber', e.target.value)}
                placeholder="1234 5678 9012 3456"
                className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  Fecha de expiración
                </label>
                <input
                  type="text"
                  value={formData.expiryDate}
                  onChange={(e) => handleInputChange('expiryDate', e.target.value)}
                  placeholder="MM/AA"
                  className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-primary mb-1">
                  CVC
                </label>
                <input
                  type="text"
                  value={formData.cvc}
                  onChange={(e) => handleInputChange('cvc', e.target.value)}
                  placeholder="123"
                  className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Nombre en la tarjeta
              </label>
              <input
                type="text"
                value={formData.cardName}
                onChange={(e) => handleInputChange('cardName', e.target.value)}
                placeholder="Juan Pérez"
                className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
            </div>
          </div>
        )}

        {selectedMethod === 'wallet' && (
          <div className="text-center py-8">
            <div className="bg-gray-50 rounded-lg p-6 border border-divider">
              <p className="text-text-secondary mb-4">Inicia tu pago con tu wallet</p>
              <div className="bg-gray-200 rounded-lg p-4 text-text-secondary">
                [Botón nativo de Apple Pay / Google Pay]
              </div>
            </div>
          </div>
        )}

        {selectedMethod === 'crypto' && (
          <div className="space-y-4">
            <h3 className="font-medium text-text-primary">Pago con Criptomonedas</h3>
            
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Moneda
              </label>
              <select
                value={formData.cryptoCurrency}
                onChange={(e) => handleInputChange('cryptoCurrency', e.target.value)}
                className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              >
                <option value="bitcoin">Bitcoin (BTC)</option>
                <option value="ethereum">Ethereum (ETH)</option>
                <option value="litecoin">Litecoin (LTC)</option>
                <option value="dogecoin">Dogecoin (DOGE)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Dirección de wallet
              </label>
              <input
                type="text"
                value={formData.walletAddress}
                onChange={(e) => handleInputChange('walletAddress', e.target.value)}
                placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
                className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
            </div>
          </div>
        )}

        {selectedMethod === 'cash' && (
          <div className="space-y-6">
            <div className="flex items-center space-x-2">
              <Calculator size={20} className="text-complement" />
              <h3 className="font-medium text-text-primary">Calculadora de Cambio</h3>
            </div>
            
            {/* Resumen del total */}
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-blue-800">Total a pagar:</span>
                <span className="text-lg font-bold text-blue-900">{formatCurrency(total)}</span>
              </div>
            </div>

            {/* Input para monto recibido */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                💵 Monto que me das
              </label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary text-lg">$</span>
                <input
                  type="number"
                  value={cashReceived || ''}
                  onChange={(e) => handleCashReceivedChange(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-8 pr-3 py-4 text-lg border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
                  step="0.01"
                  min="0"
                />
              </div>
              {cashReceived > 0 && !isSufficientAmount && (
                <p className="text-red-500 text-sm mt-1">
                  ⚠️ Monto insuficiente. Faltan {formatCurrency(total - cashReceived)}
                </p>
              )}
            </div>

            {/* Cálculo de cambio */}
            {cashReceived > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg border border-divider">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-text-secondary">Monto recibido:</span>
                    <span className="font-medium text-text-primary">{formatCurrency(cashReceived)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-text-secondary">Total a pagar:</span>
                    <span className="font-medium text-text-primary">{formatCurrency(total)}</span>
                  </div>
                  <div className="border-t border-divider pt-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-text-primary">Cambio a devolver:</span>
                      <span className={`text-lg font-bold ${
                        changeAmount >= 0 ? 'text-success' : 'text-red-500'
                      }`}>
                        {changeAmount >= 0 ? '+' : ''}{formatCurrency(changeAmount)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Botones de monto rápido */}
            <div>
              <label className="block text-sm font-medium text-text-primary mb-2">
                💡 Montos comunes
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[10, 20, 50, 100, 200, 500].map((amount) => (
                  <button
                    key={amount}
                    onClick={() => setCashReceived(amount)}
                    className={`p-2 text-sm rounded-lg border transition-colors ${
                      cashReceived === amount
                        ? 'bg-complement text-white border-complement'
                        : 'bg-bg-surface text-text-primary border-divider hover:bg-gray-50'
                    }`}
                  >
                    ${amount}
                  </button>
                ))}
              </div>
            </div>

            {/* Mensaje de confirmación */}
            {isSufficientAmount && (
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium text-green-800">
                    ✅ Pago completo. Cambio: {formatCurrency(changeAmount)}
                  </span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Fixed Footer */}
      <div className="fixed bottom-0 left-0 right-0 p-4 border-t border-divider bg-bg-surface animate-slide-in-right">
        <button 
          disabled={!isFormValid()}
          onClick={handleConfirmPayment}
          className={`w-full py-4 rounded-lg font-medium transition-all duration-300 btn-animate ${
            isFormValid()
              ? 'bg-success hover:bg-success-600 text-white hover:scale-105 hover:shadow-lg'
              : 'bg-gray-300 text-text-secondary cursor-not-allowed'
          }`}
        >
          {selectedMethod === 'cash' && cashReceived > 0 && !isSufficientAmount
            ? `Faltan ${formatCurrency(total - cashReceived)}`
            : 'Confirmar pago'
          }
        </button>
      </div>
    </div>
  );
};

export default PaymentScreen;