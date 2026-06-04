import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SessionState {
  userId: string | null
  username: string | null
  role: string | null
  gameId: string | null
  playerId: string | null
  setUser: (userId: string, username: string, role?: string) => void
  setGame: (gameId: string, playerId: string) => void
  clearGame: () => void
  logout: () => void
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      userId: null,
      username: null,
      role: null,
      gameId: null,
      playerId: null,
      setUser: (userId, username, role = 'authenticated') =>
        set({ userId, username, role }),
      setGame: (gameId, playerId) => set({ gameId, playerId }),
      clearGame: () => set({ gameId: null, playerId: null }),
      logout: () =>
        set({
          userId: null,
          username: null,
          role: null,
          gameId: null,
          playerId: null,
        }),
    }),
    { name: 'cmb-session' },
  ),
)
