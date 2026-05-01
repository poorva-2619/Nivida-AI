import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Login from './pages/Login';

// Placeholder layout for Phase 1 demonstration
const DashboardPlaceholder = ({ title, role }) => {
  const logout = useAuthStore(state => state.logout);
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm px-8 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-900">Nivida AI <span className="text-brand-600">| {role}</span></h1>
        <button onClick={logout} className="text-sm font-medium text-gray-500 hover:text-gray-700">Logout</button>
      </header>
      <main className="flex-1 p-8 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-3xl font-light text-gray-400 mb-4">{title}</h2>
          <p className="text-gray-500">More features coming in subsequent phases.</p>
        </div>
      </main>
    </div>
  );
};

const ProtectedRoute = ({ children, allowedRole }) => {
  const { isAuthenticated, role } = useAuthStore();
  
  if (!isAuthenticated) return <Navigate to="/" replace />;
  if (role !== allowedRole) return <Navigate to="/" replace />;
  
  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        
        {/* Admin Routes */}
        <Route path="/admin/*" element={
          <ProtectedRoute allowedRole="admin">
            <Routes>
              <Route path="/" element={<DashboardPlaceholder title="Admin Dashboard Placeholder" role="Administrator" />} />
            </Routes>
          </ProtectedRoute>
        } />

        {/* Vendor Routes */}
        <Route path="/vendor/*" element={
          <ProtectedRoute allowedRole="vendor">
            <Routes>
              <Route path="/" element={<DashboardPlaceholder title="Vendor Dashboard Placeholder" role="Vendor Portal" />} />
            </Routes>
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
