import axios from 'axios'
import { useSessionStore } from '@/shared/store/sessionStore'

export const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const { userId } = useSessionStore.getState()
  if (userId) {
    config.headers.set('X-User-Id', userId)
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      error.response.data?.detail === 'Unknown user'
    ) {
      useSessionStore.getState().logout()
    }
    return Promise.reject(error)
  },
)
