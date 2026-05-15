import { api } from '@/shared/api/client'
import type { User } from '@/entities/game/model/types'

export const registerUser = async (username: string): Promise<User> => {
  const response = await api.post<User>('/users/register', { username })
  return response.data
}

export const loginUser = async (username: string): Promise<User> => {
  const response = await api.post<User>('/users/login', { username })
  return response.data
}

export const listUsers = async (): Promise<User[]> => {
  const response = await api.get<User[]>('/users')
  return response.data
}
