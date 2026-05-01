import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Building2, ArrowRight, BrainCircuit } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

const Login = () => {
  const [selectedRole, setSelectedRole] = useState('vendor'); // 'admin' or 'vendor'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      login({ email, name: email.split('@')[0] }, selectedRole);
      setIsLoading(false);
      navigate(`/${selectedRole}`);
    }, 800);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 relative overflow-hidden">
      {/* Dynamic Background Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/20 rounded-full blur-[150px] mix-blend-screen" style={{ animation: 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite' }} />
      
      <div className="glass-dark w-full max-w-5xl rounded-3xl flex flex-col md:flex-row overflow-hidden z-10 mx-4 shadow-[0_0_50px_rgba(0,0,0,0.5)]">
        
        {/* Left Section - Branding */}
        <div className="w-full md:w-5/12 p-12 flex flex-col justify-between relative bg-gradient-to-br from-dark-800 to-dark-900 border-r border-white/5">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5" />
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-16">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-400 to-brand-600 flex items-center justify-center shadow-lg shadow-brand-500/30">
                <BrainCircuit className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Nivida <span className="text-brand-400">AI</span></h1>
            </div>

            <h2 className="text-4xl font-semibold leading-tight text-white mb-6">
              Intelligent <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-300 to-blue-400">
                Tender Evaluation
              </span>
            </h2>
            <p className="text-slate-400 text-lg leading-relaxed">
              Experience seamless, transparent, and AI-driven tender processing. Accelerate compliance verification with unprecedented accuracy.
            </p>
          </div>
          
          <div className="relative z-10 mt-12 flex items-center gap-4 text-sm text-slate-500 font-medium">
            <div className="h-px bg-slate-700 flex-1" />
            <span>Secure. Fast. Impartial.</span>
            <div className="h-px bg-slate-700 flex-1" />
          </div>
        </div>

        {/* Right Section - Login Form */}
        <div className="w-full md:w-7/12 p-12 bg-dark-800/50">
          <div className="max-w-md mx-auto">
            <div className="mb-10 text-center">
              <h3 className="text-2xl font-semibold text-white mb-2">Welcome Back</h3>
              <p className="text-slate-400">Select your portal and enter your credentials.</p>
            </div>

            {/* Role Selector */}
            <div className="flex p-1 bg-dark-900 rounded-xl mb-8 relative border border-white/5 shadow-inner">
              {/* Animated Background Pill */}
              <div 
                className="absolute top-1 bottom-1 w-[calc(50%-4px)] bg-dark-700 rounded-lg shadow-sm transition-transform duration-300 ease-out border border-white/10"
                style={{ transform: `translateX(${selectedRole === 'vendor' ? '0%' : '100%'})` }}
              />
              
              <button 
                onClick={() => setSelectedRole('vendor')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium z-10 transition-colors duration-200 ${selectedRole === 'vendor' ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                <Building2 className="w-4 h-4" />
                Vendor Portal
              </button>
              <button 
                onClick={() => setSelectedRole('admin')}
                className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-lg text-sm font-medium z-10 transition-colors duration-200 ${selectedRole === 'admin' ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
              >
                <ShieldCheck className="w-4 h-4" />
                Admin Portal
              </button>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                <input 
                  type="email" 
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all"
                  placeholder={selectedRole === 'admin' ? "admin@nivida.gov" : "vendor@company.com"}
                />
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="block text-sm font-medium text-slate-300">Password</label>
                  <a href="#" className="text-xs text-brand-400 hover:text-brand-300 transition-colors">Forgot password?</a>
                </div>
                <input 
                  type="password" 
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-dark-900 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 transition-all"
                  placeholder="••••••••"
                />
              </div>

              <button 
                type="submit" 
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white rounded-xl py-3.5 font-medium flex items-center justify-center gap-2 transition-all shadow-lg shadow-brand-500/20 active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed group mt-4"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </button>
            </form>
            
            <p className="text-center text-slate-500 text-sm mt-8">
              Don't have an account? <a href="#" className="text-brand-400 hover:text-brand-300 transition-colors font-medium">Request access</a>
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Login;
