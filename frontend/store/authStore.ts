'use client'

// Zustand store for the knowledge-hub admin session.
// Tokens are persisted to localStorage so a page reload keeps the operator
// signed in until the JWT expiry.
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token: string | null
  username: string | null
  expiresAt: number | null
  signIn: (token: string, username: string, expiresInSeconds: number) => void
  signOut: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      username: null,
      expiresAt: null,
      signIn: (token, username, expiresInSeconds) =>
        set({
          token,
          username,
          expiresAt: Date.now() + expiresInSeconds * 1000,
        }),
      signOut: () => set({ token: null, username: null, expiresAt: null }),
      isAuthenticated: () => {
        const { token, expiresAt } = get()
        if (!token || !expiresAt) return false
        return Date.now() < expiresAt
      },
    }),
    { name: 'knowledge-admin-session' },
  ),
)
