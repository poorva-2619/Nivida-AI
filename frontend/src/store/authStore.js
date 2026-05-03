import { create } from 'zustand'
import axios from 'axios'

export const useAuthStore = create((set) => ({
  role: null, // "admin" | "vendor" | null
  name: "",
  token: "",
  isLoggedIn: false,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('http://127.0.0.1:8000/api/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      const { access_token, role, name } = response.data;
      
      set({ 
        role, 
        name, 
        token: access_token, 
        isLoggedIn: true,
        loading: false 
      });
      return { success: true, role };
    } catch (err) {
      set({ 
        error: err.response?.data?.detail || 'Login failed',
        loading: false 
      });
      return { success: false, error: err.response?.data?.detail || 'Login failed' };
    }
  },

  logout: () => set({ role: null, name: "", token: "", isLoggedIn: false, error: null }),
}))
