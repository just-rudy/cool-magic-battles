import type { Game, Player } from '@/entities/game/model/types'

export const findPlayerByUserId = (
  game: Game,
  userId: string,
): Player | undefined => game.players.find((player) => player.user_id === userId)

export const isMyTurn = (game: Game, playerId: string | null): boolean =>
  game.status === 'in_progress' && game.cur_player_id === playerId

export const statusLabel: Record<string, string> = {
  created: 'Ожидание игроков',
  in_progress: 'Идёт игра',
  finished: 'Завершена',
}
