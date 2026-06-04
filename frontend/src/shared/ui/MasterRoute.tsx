import { Navigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getCurrentUser } from '@/entities/user/api/userApi'
import { isMasterRole } from '@/shared/lib/roles'
import { useSessionStore } from '@/shared/store/sessionStore'

export function MasterRoute({ children }: { children: React.ReactNode }) {
  const userId = useSessionStore((state) => state.userId)

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: getCurrentUser,
    enabled: Boolean(userId),
  })

  if (!userId) {
    return <Navigate to="/auth" replace />
  }

  if (profileQuery.isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-arcane-300">
        Загрузка…
      </div>
    )
  }

  if (profileQuery.isError || !isMasterRole(profileQuery.data?.role)) {
    return <Navigate to="/profile" replace />
  }

  return children
}
