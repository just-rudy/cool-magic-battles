import { api } from '@/shared/api/client'
import type { Card, Game, GameSummary } from '@/entities/game/model/types'

export const listGames = async (): Promise<GameSummary[]> => {
  const response = await api.get<GameSummary[]>('/game')
  return response.data
}

export const getGame = async (gameId: string): Promise<Game> => {
  const response = await api.get<Game>(`/game/${gameId}`)
  return response.data
}

export const createGame = async (
  hostUserId: string,
  name?: string | null,
): Promise<Game> => {
  const response = await api.post<Game>('/game/new', {
    host_user_id: hostUserId,
    name: name?.trim() || null,
  })
  return response.data
}

export const joinGame = async (
  gameId: string,
  userId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/join`, {
    user_id: userId,
  })
  return response.data
}

export const joinGameByRef = async (
  gameRef: string,
  userId: string,
): Promise<Game> => {
  const response = await api.post<Game>('/game/join', {
    user_id: userId,
    game_ref: gameRef.trim(),
  })
  return response.data
}

export const startGame = async (gameId: string): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/start`)
  return response.data
}

export interface PlayCardParams {
  cardId: string
  targetId?: string
}

export const playCard = async (
  gameId: string,
  playerId: string,
  { cardId, targetId }: PlayCardParams,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/play`, {
    player_id: playerId,
    card_id: cardId,
    target_id: targetId ?? null,
  })
  return response.data
}

export const skipDefend = async (
  gameId: string,
  playerId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/skip-defend`, {
    player_id: playerId,
  })
  return response.data
}

export const defendCard = async (
  gameId: string,
  playerId: string,
  cardId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/defend`, {
    player_id: playerId,
    card_id: cardId,
  })
  return response.data
}

export const buyCard = async (
  gameId: string,
  playerId: string,
  cardId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/buy`, {
    player_id: playerId,
    card_id: cardId,
  })
  return response.data
}

export const endTurn = async (
  gameId: string,
  playerId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/end-turn`, {
    player_id: playerId,
  })
  return response.data
}

export const finishGame = async (
  gameId: string,
  playerId: string,
): Promise<Game> => {
  const response = await api.post<Game>(`/game/${gameId}/finish`, {
    player_id: playerId,
  })
  return response.data
}

export const getPlayerCards = async (
  gameId: string,
  playerId: string,
): Promise<Card[]> => {
  const response = await api.get<Card[]>(`/game/${gameId}/players/${playerId}/cards`)
  return response.data
}
