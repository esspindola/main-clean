import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  MapPin,
  Shield,
  Eye,
  EyeOff,
  Globe,
  Clock,
  DollarSign,
  Bell,
  CreditCard,
  Download,
  HelpCircle,
  MessageSquare,
  Activity,
  LogOut,
  Trash2,
  Save,
  Camera,
  Smartphone,
  Monitor,
  Check,
  X,
  Plus,
  Edit3,
} from 'lucide-react';

interface Session {
  id: string;
  device: string;
  location: string;
  lastActive: string;
  current: boolean;
}

interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: 'Paid' | 'Pending' | 'Overdue';
}

interface PaymentCard {
  id: string;
  type: 'visa' | 'mastercard' | 'amex';
  lastFour: string;
  expiryMonth: string;
  expiryYear: string;
  holderName: string;
  isDefault: boolean;
}

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('profile');
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [showAddCardForm, setShowAddCardForm] = useState(false);
  const [editingCard, setEditingCard] = useState<PaymentCard | null>(null);
  const [showPassword, setShowPassword] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  // Profile data state
  const [profileData, setProfileData] = useState({
    name: 'John Doe',
    email: 'john.doe@company.com',
    phone: '+1 (555) 123-4567',
    address: '123 Main St, City, Country',
    role: 'Administrator',
    lastAccess: '2024-01-15 14:30',
    emailVerified: true,
    phoneVerified: false,
    twoFactorEnabled: false,
    language: 'en',
    timezone: 'America/New_York',
    dateFormat: 'MM/DD/YYYY',
    currency: 'USD',
    notifications: {
      lowStock: { email: true, inApp: true },
      newOrders: { email: true, inApp: true },
      paymentCompleted: { email: false, inApp: true },
      ocrErrors: { email: true, inApp: false },
    },
    notificationFrequency: 'immediate',
  });

  const [passwordData, setPasswordData] = useState({
    current: '',
    new: '',
    confirm: '',
  });

  const [sessions] = useState<Session[]>([
    {
      id: '1',
      device: 'Chrome on Windows',
      location: 'New York, USA',
      lastActive: '2024-01-15 14:30',
      current: true,
    },
    {
      id: '2',
      device: 'Safari on iPhone',
      location: 'Los Angeles, USA',
      lastActive: '2024-01-14 09:15',
      current: false,
    },
    {
      id: '3',
      device: 'Firefox on Mac',
      location: 'San Francisco, USA',
      lastActive: '2024-01-13 16:45',
      current: false,
    },
  ]);

  const [invoices] = useState<Invoice[]>([
    {
      id: 'INV-001',
      date: '2024-01-15',
      amount: 299.99,
      status: 'Paid',
    },
    {
      id: 'INV-002',
      date: '2024-01-10',
      amount: 149.50,
      status: 'Pending',
    },
    {
      id: 'INV-003',
      date: '2024-01-05',
      amount: 89.99,
      status: 'Overdue',
    },
  ]);

  const [paymentCards, setPaymentCards] = useState<PaymentCard[]>([
    {
      id: '1',
      type: 'visa',
      lastFour: '4242',
      expiryMonth: '12',
      expiryYear: '2025',
      holderName: 'John Doe',
      isDefault: true,
    },
    {
      id: '2',
      type: 'mastercard',
      lastFour: '8888',
      expiryMonth: '08',
      expiryYear: '2026',
      holderName: 'John Doe',
      isDefault: false,
    },
  ]);

  const [newCard, setNewCard] = useState({
    number: '',
    expiryMonth: '',
    expiryYear: '',
    cvc: '',
    holderName: '',
  });

  const sections = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'personal', name: 'Personal Data', icon: User },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'preferences', name: 'Preferences', icon: Globe },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'billing', name: 'Billing & Plan', icon: CreditCard },
    { id: 'support', name: 'Support & Help', icon: HelpCircle },
  ];

  const handleInputChange = (field: string, value: any) => {
    setProfileData(prev => ({ ...prev, [field]: value }));
  };

  const handleNestedInputChange = (parent: string, field: string, subfield: string, value: any) => {
    setProfileData(prev => {
      const parentData = prev[parent as keyof typeof prev] as any;
      return {
        ...prev,
        [parent]: {
          ...parentData,
          [field]: {
            ...(parentData?.[field] || {}),
            [subfield]: value,
          },
        },
      };
    });
  };

  const handlePasswordChange = (field: string, value: string) => {
    setPasswordData(prev => ({ ...prev, [field]: value }));
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPassword(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const handleSaveChanges = () => {
    // Save changes logic
    console.log('Saving changes...');
  };

  const handleCloseSession = (sessionId: string) => {
    // Close session logic
    console.log('Closing session:', sessionId);
  };

  const handleOpenPaymentModal = () => {
    setShowPaymentModal(true);
  };

  const handleClosePaymentModal = () => {
    setShowPaymentModal(false);
    setShowAddCardForm(false);
    setEditingCard(null);
  };

  const handleAddCard = () => {
    setShowAddCardForm(true);
    setEditingCard(null);
  };

  const handleSetDefaultCard = (cardId: string) => {
    setPaymentCards(prev => prev.map(card => ({
      ...card,
      isDefault: card.id === cardId,
    })));
  };

  const handleDeleteCard = (cardId: string) => {
    setPaymentCards(prev => prev.filter(card => card.id !== cardId));
  };

  const handleEditCard = (card: PaymentCard) => {
    setEditingCard(card);
    setShowAddCardForm(true);
  };

  const handleSaveCard = () => {
    if (editingCard) {
      setPaymentCards(prev => prev.map(card =>
        card.id === editingCard.id ? editingCard : card,
      ));
    } else {
      // Add new card logic
      const newCard: PaymentCard = {
        id: Date.now().toString(),
        type: 'visa',
        lastFour: '1234',
        expiryMonth: '12',
        expiryYear: '2025',
        holderName: 'John Doe',
        isDefault: false,
      };
      setPaymentCards(prev => [...prev, newCard]);
    }
    setShowAddCardForm(false);
    setEditingCard(null);
  };

  const getCardIcon = (type: string) => {
    switch (type) {
    case 'visa':
      return '💳';
    case 'mastercard':
      return '💳';
    case 'amex':
      return '💳';
    default:
      return '💳';
    }
  };

  const getInvoiceStatusColor = (status: string) => {
    switch (status) {
    case 'Paid':
      return 'bg-success-100 text-success-800';
    case 'Pending':
      return 'bg-warning-100 text-warning-800';
    case 'Overdue':
      return 'bg-error-100 text-error-800';
    default:
      return 'bg-gray-100 text-gray-800';
    }
  };

  const renderProfileHeader = () => (
    <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6 mb-6">
      <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
        {/* Avatar */}
        <div className="relative">
          <div className="w-20 h-20 bg-complement rounded-full flex items-center justify-center">
            <User size={32} className="text-white" />
          </div>
          <button className="absolute -bottom-1 -right-1 w-8 h-8 bg-primary rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors">
            <Camera size={16} className="text-black" />
          </button>
        </div>

        {/* User Info */}
        <div className="flex-1">
          <h2 className="text-xl font-bold text-text-primary">{profileData.name}</h2>
          <p className="text-text-secondary">{profileData.email}</p>
          <div className="flex items-center space-x-4 mt-2">
            <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-complement-100 text-complement-800">
              {profileData.role}
            </span>
            <span className="text-sm text-text-secondary">
              Last access: {profileData.lastAccess}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPersonalData = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Full Name
          </label>
          <input
            type="text"
            value={profileData.name}
            onChange={(e) => handleInputChange('name', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Email
          </label>
          <div className="flex space-x-2">
            <input
              type="email"
              value={profileData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className="flex-1 p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
            />
            <button className={`px-4 py-3 rounded-lg font-medium transition-colors ${
              profileData.emailVerified
                ? 'bg-success-100 text-success-800 cursor-default'
                : 'bg-complement hover:bg-complement-600 text-white'
            }`}>
              {profileData.emailVerified ? 'Verified' : 'Verify'}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Phone
          </label>
          <div className="flex space-x-2">
            <input
              type="tel"
              value={profileData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              className="flex-1 p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
            />
            <button className={`px-4 py-3 rounded-lg font-medium transition-colors ${
              profileData.phoneVerified
                ? 'bg-success-100 text-success-800 cursor-default'
                : 'bg-complement hover:bg-complement-600 text-white'
            }`}>
              {profileData.phoneVerified ? 'Verified' : 'Verify SMS'}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Full Address
          </label>
          <input
            type="text"
            value={profileData.address}
            onChange={(e) => handleInputChange('address', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          />
        </div>
      </div>
    </div>
  );

  const renderSecurity = () => (
    <div className="space-y-6">
      {/* Password Change */}
      <div>
        <h3 className="text-lg font-medium text-text-primary mb-4">Change Password</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Current Password
            </label>
            <div className="relative">
              <input
                type={showPassword.current ? 'text' : 'password'}
                value={passwordData.current}
                onChange={(e) => handlePasswordChange('current', e.target.value)}
                className="w-full p-3 pr-12 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('current')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
              >
                {showPassword.current ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              New Password
            </label>
            <div className="relative">
              <input
                type={showPassword.new ? 'text' : 'password'}
                value={passwordData.new}
                onChange={(e) => handlePasswordChange('new', e.target.value)}
                className="w-full p-3 pr-12 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('new')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
              >
                {showPassword.new ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Confirm New Password
            </label>
            <div className="relative">
              <input
                type={showPassword.confirm ? 'text' : 'password'}
                value={passwordData.confirm}
                onChange={(e) => handlePasswordChange('confirm', e.target.value)}
                className="w-full p-3 pr-12 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
              />
              <button
                type="button"
                onClick={() => togglePasswordVisibility('confirm')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
              >
                {showPassword.confirm ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Two Factor Authentication */}
      <div className="border-t border-divider pt-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-text-primary">Two-Factor Authentication</h3>
            <p className="text-sm text-text-secondary">Add an extra layer of security to your account</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={profileData.twoFactorEnabled}
              onChange={(e) => handleInputChange('twoFactorEnabled', e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-complement-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-complement"></div>
          </label>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="border-t border-divider pt-6">
        <h3 className="text-lg font-medium text-text-primary mb-4">Active Sessions</h3>
        <div className="space-y-3">
          {sessions.map((session) => (
            <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-divider">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                  {session.device.includes('iPhone') ? (
                    <Smartphone size={20} className="text-text-secondary" />
                  ) : (
                    <Monitor size={20} className="text-text-secondary" />
                  )}
                </div>
                <div>
                  <div className="font-medium text-text-primary">
                    {session.device}
                    {session.current && (
                      <span className="ml-2 inline-flex px-2 py-1 text-xs font-medium rounded-full bg-success-100 text-success-800">
                        Current
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-text-secondary">
                    {session.location} • {session.lastActive}
                  </div>
                </div>
              </div>
              {!session.current && (
                <button
                  onClick={() => handleCloseSession(session.id)}
                  className="px-3 py-1 text-sm text-error hover:bg-error-50 rounded transition-colors"
                >
                  Close Session
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPreferences = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Language
          </label>
          <select
            value={profileData.language}
            onChange={(e) => handleInputChange('language', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="pt">Português</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Timezone
          </label>
          <select
            value={profileData.timezone}
            onChange={(e) => handleInputChange('timezone', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          >
            <option value="America/Mexico_City">Mexico City (GMT-6)</option>
            <option value="America/New_York">New York (GMT-5)</option>
            <option value="America/Los_Angeles">Los Angeles (GMT-8)</option>
            <option value="Europe/Madrid">Madrid (GMT+1)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Date Format
          </label>
          <select
            value={profileData.dateFormat}
            onChange={(e) => handleInputChange('dateFormat', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          >
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-text-primary mb-2">
            Default Currency
          </label>
          <select
            value={profileData.currency}
            onChange={(e) => handleInputChange('currency', e.target.value)}
            className="w-full p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
          >
            <option value="USD">USD - US Dollar</option>
            <option value="MXN">MXN - Mexican Peso</option>
            <option value="EUR">EUR - Euro</option>
            <option value="GBP">GBP - British Pound</option>
          </select>
        </div>
      </div>
    </div>
  );

  const renderNotifications = () => (
    <div className="space-y-6">
      {/* Notification Types */}
      <div>
        <h3 className="text-lg font-medium text-text-primary mb-4">Notification Types</h3>
        <div className="space-y-4">
          {Object.entries(profileData.notifications).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-divider">
              <div>
                <div className="font-medium text-text-primary">
                  {key === 'lowStock' && 'Low Stock'}
                  {key === 'newOrders' && 'New Orders'}
                  {key === 'paymentCompleted' && 'Payment Completed'}
                  {key === 'ocrErrors' && 'OCR Errors'}
                </div>
                <div className="text-sm text-text-secondary">
                  {key === 'lowStock' && 'When a product has low stock'}
                  {key === 'newOrders' && 'When a new order is received'}
                  {key === 'paymentCompleted' && 'When a payment is completed'}
                  {key === 'ocrErrors' && 'When OCR processing fails'}
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={profileData.notifications[key as keyof typeof profileData.notifications].email}
                    onChange={(e) => handleNestedInputChange('notifications', key, 'email', e.target.checked)}
                    className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                  />
                  <span className="text-sm text-text-secondary">Email</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={profileData.notifications[key as keyof typeof profileData.notifications].inApp}
                    onChange={(e) => handleNestedInputChange('notifications', key, 'inApp', e.target.checked)}
                    className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement"
                  />
                  <span className="text-sm text-text-secondary">In-App</span>
                </label>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Frequency */}
      <div className="border-t border-divider pt-6">
        <h3 className="text-lg font-medium text-text-primary mb-4">Frequency</h3>
        <select
          value={profileData.notificationFrequency}
          onChange={(e) => handleInputChange('notificationFrequency', e.target.value)}
          className="w-full md:w-auto p-3 border border-divider rounded-lg focus:ring-2 focus:ring-complement focus:border-transparent bg-bg-surface text-text-primary"
        >
          <option value="immediate">Immediate</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
        </select>
      </div>
    </div>
  );

  const renderBilling = () => (
    <div className="space-y-6">
      {/* Current Plan */}
      <div className="bg-bg-surface rounded-lg border border-divider p-6">
        <h3 className="text-lg font-medium text-text-primary mb-4">Current Plan</h3>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-text-primary">Pro Plan</h4>
            <div className="text-text-secondary">$29.99/month • Up to 10,000 products</div>
          </div>
          <button className="px-4 py-2 bg-complement hover:bg-complement-600 text-white rounded-lg transition-colors">
            Upgrade
          </button>
        </div>
      </div>

      {/* Payment Method */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-text-primary">Payment Method</h3>
          <button
            onClick={handleOpenPaymentModal}
            className="bg-secondary hover:bg-secondary-600 text-white px-4 py-2 rounded-lg transition-colors">
            Update Method
          </button>
        </div>

        {/* Display default card */}
        {paymentCards.length > 0 && (
          <div className="bg-gray-50 rounded-lg p-4 border border-divider">
            <div className="flex items-center space-x-3">
              {getCardIcon(paymentCards.find(card => card.isDefault)?.type || 'visa')}
              <div>
                <div className="font-medium text-text-primary">
                  •••• •••• •••• {paymentCards.find(card => card.isDefault)?.lastFour || '****'}
                </div>
                <div className="text-sm text-text-secondary">
                  {(() => {
                    const defaultCard = paymentCards.find(card => card.isDefault);
                    if (!defaultCard) {return 'No default card';}
                    return `${defaultCard.type.charAt(0).toUpperCase() + defaultCard.type.slice(1)} • Expires ${defaultCard.expiryMonth}/${defaultCard.expiryYear}`;
                  })()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Invoices */}
      <div>
        <h3 className="text-lg font-medium text-text-primary mb-4">Invoice History</h3>
        <div className="bg-bg-surface rounded-lg border border-divider overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-divider">
              {invoices.map((invoice) => (
                <tr key={invoice.id}>
                  <td className="px-4 py-4 text-sm text-text-primary">{invoice.date}</td>
                  <td className="px-4 py-4 text-sm font-medium text-text-primary">${invoice.amount}</td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getInvoiceStatusColor(invoice.status)}`}>
                      {invoice.status}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <button className="text-complement hover:text-complement-600 text-sm font-medium">
                      <Download size={16} className="inline mr-1" />
                      Download PDF
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderSupport = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <button className="p-6 bg-gray-50 rounded-lg border border-divider hover:bg-gray-100 transition-colors text-left">
          <HelpCircle size={32} className="text-complement mb-3" />
          <h3 className="font-medium text-text-primary mb-2">Help Center</h3>
          <p className="text-sm text-text-secondary">Find answers to frequently asked questions</p>
        </button>

        <button className="p-6 bg-gray-50 rounded-lg border border-divider hover:bg-gray-100 transition-colors text-left">
          <MessageSquare size={32} className="text-complement mb-3" />
          <h3 className="font-medium text-text-primary mb-2">Send Feedback</h3>
          <p className="text-sm text-text-secondary">Share your comments and suggestions</p>
        </button>

        <button className="p-6 bg-gray-50 rounded-lg border border-divider hover:bg-gray-100 transition-colors text-left">
          <Activity size={32} className="text-complement mb-3" />
          <h3 className="font-medium text-text-primary mb-2">System Status</h3>
          <p className="text-sm text-text-secondary">Check the status of our services</p>
        </button>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
    case 'profile':
      return renderProfileHeader();
    case 'personal':
      return renderPersonalData();
    case 'security':
      return renderSecurity();
    case 'preferences':
      return renderPreferences();
    case 'notifications':
      return renderNotifications();
    case 'billing':
      return renderBilling();
    case 'support':
      return renderSupport();
    default:
      return renderProfileHeader();
    }
  };

  return (
    <div className="min-h-screen bg-bg-main pt-16">
      {/* Header */}
      <div className="bg-bg-surface shadow-sm border-b border-divider">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 hover:bg-gray-50 rounded-full transition-colors md:hidden"
              >
                <ArrowLeft size={20} className="text-text-primary" />
              </button>
              <h1 className="text-xl font-semibold text-text-primary">My Profile</h1>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

          {/* Desktop Sidebar */}
          <div className="hidden lg:block">
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-4 sticky top-24">
              <nav className="space-y-2">
                {sections.map((section) => {
                  const Icon = section.icon;
                  return (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                        activeSection === section.id
                          ? 'bg-complement-50 text-complement-700 border border-complement-200'
                          : 'text-text-secondary hover:bg-gray-50 hover:text-text-primary'
                      }`}
                    >
                      <Icon size={18} />
                      <span className="text-sm font-medium">{section.name}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Mobile/Tablet Accordion */}
          <div className="lg:hidden mb-6">
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider overflow-hidden">
              {sections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                return (
                  <div key={section.id}>
                    <button
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors border-b border-divider last:border-b-0 ${
                        isActive ? 'bg-complement-50 text-complement-700' : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <Icon size={18} />
                        <span className="font-medium">{section.name}</span>
                      </div>
                      <div className={`transform transition-transform ${isActive ? 'rotate-180' : ''}`}>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-bg-surface rounded-lg shadow-sm border border-divider p-6 mb-6">
              <h2 className="text-xl font-semibold text-text-primary mb-6">
                {sections.find(s => s.id === activeSection)?.name}
              </h2>
              {renderContent()}
            </div>
          </div>
        </div>
      </div>

      {/* Fixed Footer */}
      <div className="fixed bottom-0 left-0 right-0 bg-bg-surface border-t border-divider p-4 md:pl-64">
        <div className="max-w-7xl mx-auto flex items-center justify-center">
          <button
            onClick={handleSaveChanges}
            className="bg-primary hover:bg-primary-600 text-black font-medium py-3 px-8 rounded-lg transition-colors flex items-center space-x-2"
          >
            <Save size={16} />
            <span>Save Changes</span>
          </button>
        </div>
      </div>

      {/* Payment Method Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-bg-surface rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-divider">
              <h3 className="text-lg font-medium text-text-primary">
                Manage Payment Methods
              </h3>
              <button
                onClick={handleClosePaymentModal}
                className="p-2 hover:bg-gray-50 rounded-full transition-colors"
              >
                <X size={20} className="text-text-secondary" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <p className="text-text-secondary">Payment modal content goes here.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfilePage;
