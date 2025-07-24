import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { usePlugins } from '../contexts/PluginContext';
import { 
  Settings, 
  User, 
  Shield, 
  Database, 
  Palette, 
  Bell, 
  Globe, 
  Save,
  ArrowLeft,
  Eye,
  EyeOff,
  Check,
  X
} from 'lucide-react';

interface SettingsSection {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  description: string;
}

const SettingsPage: React.FC = () => {
  const { user } = useAuth();
  const { isPluginActive, togglePlugin } = usePlugins();
  const [activeSection, setActiveSection] = useState('general');
  const [showPassword, setShowPassword] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  // Form states
  const [generalSettings, setGeneralSettings] = useState({
    companyName: 'ZatoBox',
    language: 'es',
    timezone: 'America/Mexico_City',
    currency: 'MXN'
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    sessionTimeout: 30,
    passwordExpiry: 90,
    loginAttempts: 5
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    lowStockAlerts: true,
    salesReports: true,
    systemUpdates: false
  });

  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: 'light',
    sidebarCollapsed: false,
    animations: true,
    compactMode: false
  });

  const sections: SettingsSection[] = [
    {
      id: 'general',
      title: 'General',
      icon: Settings,
      description: 'Configuración básica del sistema'
    },
    {
      id: 'profile',
      title: 'Perfil',
      icon: User,
      description: 'Información personal y credenciales'
    },
    {
      id: 'security',
      title: 'Seguridad',
      icon: Shield,
      description: 'Configuración de seguridad y privacidad'
    },
    {
      id: 'notifications',
      title: 'Notificaciones',
      icon: Bell,
      description: 'Preferencias de notificaciones'
    },
    {
      id: 'appearance',
      title: 'Apariencia',
      icon: Palette,
      description: 'Tema y personalización visual'
    },
    {
      id: 'plugins',
      title: 'Plugins',
      icon: Database,
      description: 'Gestión de módulos y extensiones'
    },
    {
      id: 'system',
      title: 'Sistema',
      icon: Globe,
      description: 'Configuración avanzada del sistema'
    }
  ];

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus('idle');
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Configuración de la Empresa</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Nombre de la Empresa
            </label>
            <input
              type="text"
              value={generalSettings.companyName}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, companyName: e.target.value }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Moneda
            </label>
            <select
              value={generalSettings.currency}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, currency: e.target.value }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="MXN">Peso Mexicano (MXN)</option>
              <option value="USD">Dólar Estadounidense (USD)</option>
              <option value="EUR">Euro (EUR)</option>
            </select>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Configuración Regional</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Idioma
            </label>
            <select
              value={generalSettings.language}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, language: e.target.value }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="es">Español</option>
              <option value="en">English</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Zona Horaria
            </label>
            <select
              value={generalSettings.timezone}
              onChange={(e) => setGeneralSettings(prev => ({ ...prev, timezone: e.target.value }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value="America/Mexico_City">Ciudad de México</option>
              <option value="America/New_York">Nueva York</option>
              <option value="Europe/Madrid">Madrid</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Información Personal</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Nombre Completo
            </label>
            <input
              type="text"
              defaultValue={user?.fullName || ''}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Email
            </label>
            <input
              type="email"
              defaultValue={user?.email || ''}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Cambiar Contraseña</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Contraseña Actual
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                className="w-full px-3 py-2 pr-10 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Nueva Contraseña
              </label>
              <input
                type="password"
                className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Confirmar Contraseña
              </label>
              <input
                type="password"
                className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Autenticación</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-divider rounded-lg">
            <div>
              <h4 className="font-medium text-text-primary">Autenticación de Dos Factores</h4>
              <p className="text-sm text-text-secondary">Añade una capa extra de seguridad</p>
            </div>
            <button
              onClick={() => setSecuritySettings(prev => ({ ...prev, twoFactorAuth: !prev.twoFactorAuth }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                securitySettings.twoFactorAuth ? 'bg-primary' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  securitySettings.twoFactorAuth ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Configuración de Sesión</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Tiempo de Sesión (minutos)
            </label>
            <input
              type="number"
              value={securitySettings.sessionTimeout}
              onChange={(e) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-secondary mb-2">
              Intentos de Login
            </label>
            <input
              type="number"
              value={securitySettings.loginAttempts}
              onChange={(e) => setSecuritySettings(prev => ({ ...prev, loginAttempts: parseInt(e.target.value) }))}
              className="w-full px-3 py-2 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Notificaciones por Email</h3>
        <div className="space-y-4">
          {Object.entries(notificationSettings).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between p-4 border border-divider rounded-lg">
              <div>
                <h4 className="font-medium text-text-primary">
                  {key === 'emailNotifications' && 'Notificaciones Generales'}
                  {key === 'lowStockAlerts' && 'Alertas de Stock Bajo'}
                  {key === 'salesReports' && 'Reportes de Ventas'}
                  {key === 'systemUpdates' && 'Actualizaciones del Sistema'}
                </h4>
                <p className="text-sm text-text-secondary">
                  {key === 'emailNotifications' && 'Recibe notificaciones importantes por email'}
                  {key === 'lowStockAlerts' && 'Alerta cuando los productos tengan stock bajo'}
                  {key === 'salesReports' && 'Reportes diarios de ventas'}
                  {key === 'systemUpdates' && 'Notificaciones sobre actualizaciones del sistema'}
                </p>
              </div>
              <button
                onClick={() => setNotificationSettings(prev => ({ ...prev, [key]: !value }))}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  value ? 'bg-primary' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    value ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Tema</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {['light', 'dark', 'auto'].map((theme) => (
            <button
              key={theme}
              onClick={() => setAppearanceSettings(prev => ({ ...prev, theme }))}
              className={`p-4 border rounded-lg text-left transition-colors ${
                appearanceSettings.theme === theme
                  ? 'border-primary bg-primary-50'
                  : 'border-divider hover:border-primary'
              }`}
            >
              <div className="font-medium text-text-primary capitalize">{theme}</div>
              <div className="text-sm text-text-secondary">
                {theme === 'light' && 'Tema claro'}
                {theme === 'dark' && 'Tema oscuro'}
                {theme === 'auto' && 'Automático'}
              </div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Interfaz</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-divider rounded-lg">
            <div>
              <h4 className="font-medium text-text-primary">Animaciones</h4>
              <p className="text-sm text-text-secondary">Mostrar animaciones en la interfaz</p>
            </div>
            <button
              onClick={() => setAppearanceSettings(prev => ({ ...prev, animations: !prev.animations }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                appearanceSettings.animations ? 'bg-primary' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  appearanceSettings.animations ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          <div className="flex items-center justify-between p-4 border border-divider rounded-lg">
            <div>
              <h4 className="font-medium text-text-primary">Modo Compacto</h4>
              <p className="text-sm text-text-secondary">Reducir el espaciado en la interfaz</p>
            </div>
            <button
              onClick={() => setAppearanceSettings(prev => ({ ...prev, compactMode: !prev.compactMode }))}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                appearanceSettings.compactMode ? 'bg-primary' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  appearanceSettings.compactMode ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPluginSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Módulos Disponibles</h3>
        <div className="space-y-4">
          {[
            { id: 'smart-inventory', name: 'Smart Inventory', description: 'Gestión inteligente de inventario con IA' },
            { id: 'ocr-module', name: 'OCR Documents', description: 'Procesamiento de documentos con OCR' },
            { id: 'pos-integration', name: 'POS Integration', description: 'Integración con sistemas POS' }
          ].map((plugin) => (
            <div key={plugin.id} className="flex items-center justify-between p-4 border border-divider rounded-lg">
              <div>
                <h4 className="font-medium text-text-primary">{plugin.name}</h4>
                <p className="text-sm text-text-secondary">{plugin.description}</p>
              </div>
              <button
                onClick={() => togglePlugin(plugin.id)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isPluginActive(plugin.id) ? 'bg-primary' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isPluginActive(plugin.id) ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderSystemSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Información del Sistema</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-divider rounded-lg">
            <h4 className="font-medium text-text-primary mb-2">Versión</h4>
            <p className="text-sm text-text-secondary">ZatoBox v2.0.0</p>
          </div>
          <div className="p-4 border border-divider rounded-lg">
            <h4 className="font-medium text-text-primary mb-2">Última Actualización</h4>
            <p className="text-sm text-text-secondary">24 de Julio, 2025</p>
          </div>
          <div className="p-4 border border-divider rounded-lg">
            <h4 className="font-medium text-text-primary mb-2">Base de Datos</h4>
            <p className="text-sm text-text-secondary">SQLite v3.45.0</p>
          </div>
          <div className="p-4 border border-divider rounded-lg">
            <h4 className="font-medium text-text-primary mb-2">Estado</h4>
            <p className="text-sm text-success">Operativo</p>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-text-primary mb-4">Mantenimiento</h3>
        <div className="space-y-4">
          <button className="w-full p-4 border border-divider rounded-lg text-left hover:border-primary transition-colors">
            <h4 className="font-medium text-text-primary">Respaldar Base de Datos</h4>
            <p className="text-sm text-text-secondary">Crear una copia de seguridad de todos los datos</p>
          </button>
          <button className="w-full p-4 border border-divider rounded-lg text-left hover:border-primary transition-colors">
            <h4 className="font-medium text-text-primary">Limpiar Cache</h4>
            <p className="text-sm text-text-secondary">Eliminar archivos temporales del sistema</p>
          </button>
          <button className="w-full p-4 border border-error rounded-lg text-left hover:border-error-600 transition-colors">
            <h4 className="font-medium text-error">Restablecer Configuración</h4>
            <p className="text-sm text-text-secondary">Volver a la configuración por defecto</p>
          </button>
        </div>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings();
      case 'profile':
        return renderProfileSettings();
      case 'security':
        return renderSecuritySettings();
      case 'notifications':
        return renderNotificationSettings();
      case 'appearance':
        return renderAppearanceSettings();
      case 'plugins':
        return renderPluginSettings();
      case 'system':
        return renderSystemSettings();
      default:
        return renderGeneralSettings();
    }
  };

  return (
    <div className="min-h-screen bg-bg-main">
      {/* Header */}
      <div className="bg-bg-surface border-b border-divider">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.history.back()}
                className="p-2 text-text-secondary hover:text-text-primary transition-colors"
              >
                <ArrowLeft size={20} />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-text-primary">Configuración</h1>
                <p className="text-sm text-text-secondary">Gestiona la configuración de ZatoBox</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {saveStatus === 'success' && (
                <div className="flex items-center space-x-2 text-success">
                  <Check size={16} />
                  <span className="text-sm">Guardado</span>
                </div>
              )}
              {saveStatus === 'error' && (
                <div className="flex items-center space-x-2 text-error">
                  <X size={16} />
                  <span className="text-sm">Error</span>
                </div>
              )}
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex items-center space-x-2 px-4 py-2 bg-primary text-black font-medium rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50"
              >
                <Save size={16} />
                <span>{isSaving ? 'Guardando...' : 'Guardar'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <nav className="space-y-2">
              {sections.map((section) => {
                const Icon = section.icon;
                return (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                      activeSection === section.id
                        ? 'bg-primary text-black'
                        : 'text-text-secondary hover:text-text-primary hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={20} />
                    <div>
                      <div className="font-medium">{section.title}</div>
                      <div className="text-sm opacity-75">{section.description}</div>
                    </div>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-bg-surface border border-divider rounded-lg p-6">
              {renderContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage; 