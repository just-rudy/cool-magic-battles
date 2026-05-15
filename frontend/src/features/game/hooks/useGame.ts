import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  buyCard,
  endTurn,
  finishGame,
  getGame,
  playCard,
  startGame,
} from '@/entities/game/api/gameApi'

export const gameQueryKey = (gameId: string) => ['game', gameId] as const

export function useGame(gameId: string | null, enabled = true) {
  return useQuery({
    queryKey: gameId ? gameQueryKey(gameId) : ['game', 'empty'],
    queryFn: () => getGame(gameId!),
    enabled: Boolean(gameId) && enabled,
    refetchInterval: (query) =>
      query.state.data?.status === 'in_progress' ? 2000 : false,
  })
}

export function useGameActions(gameId: string, playerId: string) {
  const queryClient = useQueryClient()

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: gameQueryKey(gameId) })
  }

  const play = useMutation({
    mutationFn: (cardId: string) => playCard(gameId, playerId, cardId),
    onSuccess: invalidate,
  })

  const buy = useMutation({
    mutationFn: (cardId: string) => buyCard(gameId, playerId, cardId),
    onSuccess: invalidate,
  })

  const end = useMutation({
    mutationFn: () => endTurn(gameId, playerId),
    onSuccess: invalidate,
  })

  const start = useMutation({
    mutationFn: () => startGame(gameId),
    onSuccess: invalidate,
  })

  const finish = useMutation({
    mutationFn: () => finishGame(gameId, playerId),
    onSuccess: invalidate,
  })

  const pending =
    play.isPending ||
    buy.isPending ||
    end.isPending ||
    start.isPending ||
    finish.isPending

  const error =
    play.error || buy.error || end.error || start.error || finish.error

  return { play, buy, end, start, finish, pending, error }
}
