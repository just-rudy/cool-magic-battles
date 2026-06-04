import { api } from '@/shared/api/client'
import type { User, UserProfile } from '@/entities/game/model/types'

export interface RegisterPayload {
  username: string
  password: string
  password_confirm: string
}

export interface LoginPayload {
  username: string
  password: string
}

export const registerUser = async (payload: RegisterPayload): Promise<User> => {
  const response = await api.post<User>('/users/register', payload)
  return response.data
}

export const loginUser = async (payload: LoginPayload): Promise<User> => {
  const response = await api.post<User>('/users/login', payload)
  return response.data
}

export const getCurrentUser = async (): Promise<UserProfile> => {
  const response = await api.get<UserProfile>('/users/me')
  return response.data
}
