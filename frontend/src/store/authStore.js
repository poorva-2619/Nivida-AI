import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  role: null, // 'admin' or 'vendor'
  login: (userData, role) => set({ user: userData, isAuthenticated: true, role }),
  logout: () => set({ user: null, isAuthenticated: false, role: null }),
}));
