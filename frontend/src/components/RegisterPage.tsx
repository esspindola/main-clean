import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    acceptTerms: false
  });

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (!formData.acceptTerms) {
      setError('You must accept the Terms and Conditions');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await register({
        fullName: formData.fullName,
        email: formData.email,
        password: formData.password,
        phone: formData.phone
      });
      navigate('/');
    } catch (error: any) {
      setError(error.message || 'Error registering user');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-main">
      {/* Desktop Layout (≥1024px) */}
      <div className="hidden lg:flex lg:items-center lg:justify-center lg:min-h-screen lg:p-6">
        <div className="w-full max-w-md bg-bg-surface rounded-lg shadow-sm border border-divider p-6">
          {/* Title and Description */}
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-text-primary mb-4">
              Create Account
            </h1>
            <p className="text-sm text-text-secondary">
              Sign up to start managing your inventory
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) => handleInputChange('fullName', e.target.value)}
                placeholder="Your full name"
                className="w-full h-11 px-4 border border-divider rounded focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary hover:shadow-sm"
                required
              />
            </div>

            {/* Email */}
            <div>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                placeholder="example@email.com"
                className="w-full h-11 px-4 border border-divider rounded focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary hover:shadow-sm"
                required
              />
            </div>

            {/* Password */}
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                placeholder="at least 8 characters"
                className="w-full h-11 px-4 pr-12 border border-divider rounded focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary hover:shadow-sm"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            {/* Confirm Password */}
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                placeholder="confirm your password"
                className="w-full h-11 px-4 pr-12 border border-divider rounded focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary hover:shadow-sm"
                required
                minLength={8}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
              >
                {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>

            {/* Phone */}
            <div>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                placeholder="phone number (optional)"
                className="w-full h-11 px-4 border border-divider rounded focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary hover:shadow-sm"
              />
            </div>

            {/* Terms and Conditions */}
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="acceptTerms"
                checked={formData.acceptTerms}
                onChange={(e) => handleInputChange('acceptTerms', e.target.checked)}
                className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement mt-1"
                required
              />
              <label htmlFor="acceptTerms" className="text-sm text-text-secondary">
                I agree to the{' '}
                <button
                  type="button"
                  className="text-complement hover:text-complement-600 font-medium transition-colors"
                >
                  Terms and Conditions
                </button>
                {' '}and{' '}
                <button
                  type="button"
                  className="text-complement hover:text-complement-600 font-medium transition-colors"
                >
                  Privacy Policy
                </button>
              </label>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-11 bg-primary hover:bg-primary-600 text-black font-medium rounded transition-all duration-150 ease-in-out hover:shadow-md transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          {/* Sign In Link */}
          <div className="text-center mt-6">
            <p className="text-sm text-text-secondary">
              Already have an account?{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-complement hover:text-complement-600 font-medium transition-colors"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </div>

      {/* Mobile Layout (<1024px) */}
      <div className="lg:hidden min-h-screen p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-sm">F</span>
            </div>
            <span className="text-xl font-bold text-text-primary">FrontPOSw</span>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-sm space-y-6">
            {/* Title and Description */}
            <div className="text-center">
              <h1 className="text-2xl font-bold text-text-primary mb-2">
                Create Account
              </h1>
              <p className="text-sm text-text-secondary">
                Sign up to start managing your inventory
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Full Name */}
              <div>
                <input
                  type="text"
                  value={formData.fullName}
                  onChange={(e) => handleInputChange('fullName', e.target.value)}
                  placeholder="Your full name"
                  className="w-full h-11 px-4 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary"
                  required
                />
              </div>

              {/* Email */}
              <div>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="example@email.com"
                  className="w-full h-11 px-4 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary"
                  required
                />
              </div>

              {/* Password */}
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={(e) => handleInputChange('password', e.target.value)}
                  placeholder="at least 8 characters"
                  className="w-full h-11 px-4 pr-12 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              {/* Confirm Password */}
              <div className="relative">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                  placeholder="confirm your password"
                  className="w-full h-11 px-4 pr-12 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary"
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-secondary hover:text-text-primary transition-colors"
                >
                  {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>

              {/* Phone */}
              <div>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  placeholder="phone number (optional)"
                  className="w-full h-11 px-4 border border-divider rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-150 ease-in-out bg-bg-surface text-text-primary placeholder-text-secondary"
                />
              </div>

              {/* Terms and Conditions */}
              <div className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  id="acceptTermsMobile"
                  checked={formData.acceptTerms}
                  onChange={(e) => handleInputChange('acceptTerms', e.target.checked)}
                  className="w-4 h-4 text-complement border-gray-300 rounded focus:ring-complement mt-1"
                  required
                />
                <label htmlFor="acceptTermsMobile" className="text-sm text-text-secondary">
                  I agree to the{' '}
                  <button
                    type="button"
                    className="text-complement hover:text-complement-600 font-medium transition-colors"
                  >
                    Terms and Conditions
                  </button>
                  {' '}and{' '}
                  <button
                    type="button"
                    className="text-complement hover:text-complement-600 font-medium transition-colors"
                  >
                    Privacy Policy
                  </button>
                </label>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 bg-error-50 border border-error-200 rounded-lg text-error-700 text-sm">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-11 bg-primary hover:bg-primary-600 text-black font-medium rounded-lg transition-all duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Creating account...' : 'Create Account'}
              </button>
            </form>

            {/* Sign In Link */}
            <div className="text-center">
              <p className="text-sm text-text-secondary">
                Already have an account?{' '}
                <button
                  onClick={() => navigate('/login')}
                  className="text-complement hover:text-complement-600 font-medium transition-colors"
                >
                  Sign in
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;