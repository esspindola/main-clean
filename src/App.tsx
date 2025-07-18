import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import SideMenu from './components/SideMenu';
import HomePage from './components/HomePage';
import InventoryPage from './components/InventoryPage';
import NewProductPage from './components/NewProductPage';
import EditProductPage from './components/EditProductPage';
// import OCRResultPage from './components/OCRResultPage';
import ProfilePage from './components/ProfilePage';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Auth Routes - No sidebar */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Main App Routes - With sidebar */}
          <Route path="/*" element={
            <ProtectedRoute>
              <div className="min-h-screen bg-bg-main">
                {/* Side Menu - only visible on desktop */}
                <SideMenu />
                
                {/* Main content with left padding on desktop to account for sidebar */}
                <main className="pt-16 md:pt-0 md:pl-64">
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/inventory" element={<InventoryPage />} />
                    <Route path="/new-product" element={<NewProductPage />} />
                    <Route path="/edit-product/:id" element={<EditProductPage />} />
                    {/* <Route path="/ocr-result" element={<OCRResultPage />} /> */}
                    <Route path="/profile" element={<ProfilePage />} />
                    {/* Redirige rutas inválidas a Home */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </main>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;