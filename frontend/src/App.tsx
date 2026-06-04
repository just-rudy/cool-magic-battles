import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppProviders } from '@/app/providers'
import { ProtectedRoute } from '@/shared/ui/ProtectedRoute'
import { AuthPage } from '@/pages/AuthPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { CatalogEditPage } from '@/pages/CatalogEditPage'
import { LobbyPage } from '@/pages/LobbyPage'
import { GamePage } from '@/pages/GamePage'
import { MasterRoute } from '@/shared/ui/MasterRoute'

function App() {
  return (
    <AppProviders>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<AuthPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/catalog/edit"
            element={
              <ProtectedRoute>
                <MasterRoute>
                  <CatalogEditPage />
                </MasterRoute>
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <LobbyPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/game/:gameId"
            element={
              <ProtectedRoute>
                <GamePage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AppProviders>
  )
}

export default App
