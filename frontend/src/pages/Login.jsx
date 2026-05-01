import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export default function Login() {
  const [selectedRole, setSelectedRole] = useState('admin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    login(selectedRole, email || 'User', 'mock-token-123');
    if (selectedRole === 'admin') {
      navigate('/admin/dashboard');
    } else {
      navigate('/vendor/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-navy text-white flex-col justify-center items-start p-16">
        <div className="max-w-xl">
          <h1 className="text-7xl font-bold mb-2">निविदाAI</h1>
          <h2 className="text-3xl italic text-gold mb-6">NividaAI</h2>
          <p className="text-xl text-gray-300 mb-12">Automated. Explainable. Audit-Ready.</p>
          
          <div className="flex flex-wrap gap-4">
            <span className="px-4 py-2 rounded-full border border-gold/50 bg-gold/10 text-gold text-sm font-semibold tracking-wide">
              OCR Powered
            </span>
            <span className="px-4 py-2 rounded-full border border-gold/50 bg-gold/10 text-gold text-sm font-semibold tracking-wide">
              AI Evaluated
            </span>
            <span className="px-4 py-2 rounded-full border border-gold/50 bg-gold/10 text-gold text-sm font-semibold tracking-wide">
              Fraud Detected
            </span>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-8 bg-gray-50">
        <div className="w-full max-w-md">
          <div className="mb-8 text-center lg:text-left">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p className="text-gray-600">Select your role to continue</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            {/* Role Selector */}
            <div className="grid grid-cols-2 gap-4">
              {/* Administrator Card */}
              <div 
                onClick={() => setSelectedRole('admin')}
                className={`cursor-pointer border-2 rounded-xl p-4 transition-all duration-200 ${selectedRole === 'admin' ? 'border-navy bg-navy text-white shadow-lg' : 'border-gray-200 bg-white hover:border-navy/50'}`}
              >
                <div className="flex flex-col items-center text-center space-y-2">
                  <svg className={`w-8 h-8 ${selectedRole === 'admin' ? 'text-gold' : 'text-navy'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <div>
                    <div className="font-bold">Administrator</div>
                    <div className={`text-xs mt-1 ${selectedRole === 'admin' ? 'text-gray-300' : 'text-gray-500'}`}>Government Officer Portal</div>
                  </div>
                </div>
              </div>

              {/* Vendor Card */}
              <div 
                onClick={() => setSelectedRole('vendor')}
                className={`cursor-pointer border-2 rounded-xl p-4 transition-all duration-200 ${selectedRole === 'vendor' ? 'border-navy bg-navy text-white shadow-lg' : 'border-gray-200 bg-white hover:border-navy/50'}`}
              >
                <div className="flex flex-col items-center text-center space-y-2">
                  <svg className={`w-8 h-8 ${selectedRole === 'vendor' ? 'text-gold' : 'text-navy'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <div>
                    <div className="font-bold">Vendor</div>
                    <div className={`text-xs mt-1 ${selectedRole === 'vendor' ? 'text-gray-300' : 'text-gray-500'}`}>Bid Submission Portal</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-4 pt-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition-colors text-black"
                  placeholder="name@government.in"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-navy focus:border-navy outline-none transition-colors text-black"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <button 
              type="submit" 
              className="w-full bg-gold hover:bg-yellow-500 text-navy font-bold text-lg py-3 rounded-lg shadow-md transition-colors"
            >
              Login
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
