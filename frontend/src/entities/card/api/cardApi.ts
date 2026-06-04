import { api } from '@/shared/api/client'
import type { Card, CardType } from '@/entities/game/model/types'

export interface CardPayload {
  title: string
  creature: string
  card_type_id: string
  power: number
  echo: number
  cost: number
  cool_points: number
}

export const listCatalogCards = async (): Promise<Card[]> => {
  const response = await api.get<Card[]>('/cards')
  return response.data
}

export const listCardTypes = async (): Promise<CardType[]> => {
  const response = await api.get<CardType[]>('/cards/types')
  return response.data
}

export const createCatalogCard = async (payload: CardPayload): Promise<Card> => {
  const response = await api.post<Card>('/cards', payload)
  return response.data
}

export const updateCatalogCard = async (
  cardId: string,
  payload: CardPayload,
): Promise<Card> => {
  const response = await api.put<Card>(`/cards/${cardId}`, payload)
  return response.data
}

export const deleteCatalogCard = async (cardId: string): Promise<void> => {
  await api.delete(`/cards/${cardId}`)
}
