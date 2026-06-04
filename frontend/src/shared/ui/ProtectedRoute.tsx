import { Navigate } from 'react-router-dom'
import { useSessionStore } from '@/shared/store/sessionStore'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const userId = useSessionStore((state) => state.userId)

  if (!userId) {
    return <Navigate to="/auth" replace />
  }

  return children
}
