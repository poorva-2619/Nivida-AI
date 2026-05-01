import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  role: null, // "admin" | "vendor" | null
  name: "",
  token: "",
  isLoggedIn: false,
  login: (role, name, token) => set({ role, name, token, isLoggedIn: true }),
  logout: () => set({ role: null, name: "", token: "", isLoggedIn: false }),
}))
