import type { Game, Player } from '@/entities/game/model/types'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { CardTile } from '@/shared/ui/CardTile'
import { isMyTurn } from '@/shared/lib/game'
import { PlayersBar } from '@/features/game/components/PlayersBar'
import { useGameActions } from '@/features/game/hooks/useGame'
import { getPlayerCards } from '@/entities/game/api/gameApi'

interface GameBoardProps {
  game: Game
  myPlayer: Player
}

export function GameBoard({ game, myPlayer }: GameBoardProps) {
  const myTurn = isMyTurn(game, myPlayer.id)
  const { play, buy, end, start, finish, pending, error } = useGameActions(
    game.id,
    myPlayer.id,
  )
  const [showOwnCards, setShowOwnCards] = useState(false)
  const activePlayer = game.players.find((player) => player.id === game.cur_player_id)

  const { data: ownCards, isLoading: isLoadingOwnCards } = useQuery({
    queryKey: ['player-cards', game.id, myPlayer.id],
    queryFn: () => getPlayerCards(game.id, myPlayer.id),
    enabled: showOwnCards && game.status === 'finished',
    staleTime: Infinity,
  })

  // Извлекаем текст ошибки из разных типов ошибок
  const getErrorMessage = (err: unknown): string | null => {
    if (!err) return null

    // Axios error с response.data.detail
    if (typeof err === 'object' && err !== null && 'response' in err) {
      const axiosError = err as { response?: { data?: { detail?: string } } }
      if (axiosError.response?.data?.detail) {
        return axiosError.response.data.detail
      }
    }

    // Error object
    if (err instanceof Error) {
      return err.message
    }

    // String
    if (typeof err === 'string') {
      return err
    }

    return 'Произошла ошибка'
  }

  const actionError = getErrorMessage(error)

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-arcane-300">
              Статус
            </p>
            <p className="text-xl font-semibold text-white">
              {game.status === 'created'
                ? 'Ожидание игроков'
                : game.status === 'in_progress'
                  ? 'Идёт игра'
                  : 'Завершена'}
            </p>
          </div>
          <div className="text-sm text-arcane-300">
            <p>Ход № {game.cur_turn + 1}</p>
            <p>Колода: {game.deck_count} · Сброс: {game.banish_count}</p>
          </div>
        </div>

        {game.status === 'finished' && game.winner && (
          <div className="mt-4 rounded-xl border border-emerald-400/40 bg-emerald-950/30 px-4 py-3 text-sm text-emerald-100">
            Победитель: <span className="font-semibold">{game.winner.nickname}</span>
            {' '}· Очки крутости: {game.winner.cool_points}
            {' '}· Карт: {game.winner.cards_count}
          </div>
        )}

        {game.pending_attack && (
          <div className="mt-4 rounded-xl border border-red-400/40 bg-red-950/30 px-4 py-3 text-sm text-red-100">
            <div className="flex items-center gap-2">
              <span className="text-lg">⚔️</span>
              <div>
                <div className="font-semibold">Атака в процессе!</div>
                <div className="text-xs text-red-200/80">
                  Урон: {game.pending_attack.damage} · Защитник может сыграть DEF карту
                </div>
              </div>
            </div>
          </div>
        )}

        {game.status === 'created' && (
          <button
            type="button"
            disabled={pending || game.players.length < 1}
            onClick={() => start.mutate()}
            className="mt-4 rounded-xl bg-arcane-500 px-5 py-3 font-semibold text-white transition hover:bg-arcane-400 disabled:opacity-50"
          >
            Начать игру
          </button>
        )}

        {game.status === 'in_progress' && myTurn && (
          <button
            type="button"
            disabled={pending}
            onClick={() => end.mutate()}
            className="mt-4 rounded-xl bg-gold-500 px-5 py-3 font-semibold text-arcane-950 transition hover:bg-gold-400 disabled:opacity-50"
          >
            Завершить ход
          </button>
        )}

        {game.status !== 'finished' && (
          <button
            type="button"
            disabled={pending}
            onClick={() => finish.mutate()}
            className="mt-4 ml-0 rounded-xl border border-red-400/50 bg-red-950/40 px-5 py-3 font-semibold text-red-100 transition hover:bg-red-900/60 disabled:opacity-50 sm:ml-3"
          >
            Завершить игру
          </button>
        )}

        {game.status === 'finished' && (
          <button
            type="button"
            disabled={isLoadingOwnCards}
            onClick={() => setShowOwnCards((value) => !value)}
            className="mt-4 ml-0 rounded-xl border border-cyan-400/50 bg-cyan-950/40 px-5 py-3 font-semibold text-cyan-100 transition hover:bg-cyan-900/60 disabled:opacity-50 sm:ml-3"
          >
            {showOwnCards ? 'Скрыть мои карты' : 'Показать мои карты'}
          </button>
        )}

        {actionError && (
          <p className="mt-3 rounded-lg border border-red-400/40 bg-red-950/40 px-3 py-2 text-sm text-red-200">
            {actionError}
          </p>
        )}
      </section>

      <PlayersBar game={game} myPlayerId={myPlayer.id} />

      {game.status === 'finished' && (
        <section className="rounded-2xl border border-sky-500/30 bg-sky-950/20 p-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-sky-300">
                Итоги партии
              </p>
              <p className="text-xl font-semibold text-white">
                Результаты всех игроков
              </p>
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {game.players
              .slice()
              .sort((a, b) =>
                b.cool_points !== a.cool_points
                  ? b.cool_points - a.cool_points
                  : b.cards_count - a.cards_count,
              )
              .map((player, index) => (
                <div
                  key={player.id}
                  className="rounded-2xl border border-white/10 bg-white/5 p-4"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm text-sky-300">#{index + 1}</p>
                      <p className="text-lg font-semibold text-white">
                        {player.nickname}
                      </p>
                    </div>
                    {game.winner?.player_id === player.id && (
                      <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300">
                        Победитель
                      </span>
                    )}
                  </div>
                  <div className="mt-3 grid gap-2 text-sm text-arcane-300">
                    <div className="flex items-center justify-between">
                      <span>Очки крутости</span>
                      <span className="font-semibold text-white">
                        {player.cool_points}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Всего карт</span>
                      <span className="font-semibold text-white">
                        {player.cards_count}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Рука</span>
                      <span className="font-semibold text-white">
                        {player.hand.length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Стол</span>
                      <span className="font-semibold text-white">
                        {player.table.length}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold text-white">Рынок</h2>
        <div className="flex flex-wrap gap-3">
          {game.market.length === 0 && (
            <p className="text-arcane-300">Рынок пуст</p>
          )}
          {game.market.map((card) => (
            <CardTile
              key={card.id}
              card={card}
              disabled={!myTurn || pending}
              onClick={() => buy.mutate(card.id)}
            />
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-white">
          Ваша рука ({myPlayer.hand.length})
        </h2>
        <div className="flex flex-wrap gap-3">
          {myPlayer.hand.length === 0 && (
            <p className="text-arcane-300">На руке нет карт</p>
          )}
          {myPlayer.hand.map((card) => (
            <CardTile
              key={card.id}
              card={card}
              highlight
              disabled={!myTurn || pending}
              onClick={() => play.mutate(card.id)}
            />
          ))}
        </div>
      </section>

      {activePlayer && activePlayer.table.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-semibold text-white">
            {activePlayer.id === myPlayer.id
              ? `Ваш стол (${activePlayer.table.length})`
              : `Стол игрока ${activePlayer.nickname} (${activePlayer.table.length})`}
          </h2>
          <div className="flex flex-wrap gap-3">
            {activePlayer.table.map((card) => (
              <CardTile key={card.id} card={card} disabled />
            ))}
          </div>
        </section>
      )}

      {showOwnCards && (
        <section>
          <div className="mb-3 flex items-center justify-between gap-4">
            <h2 className="text-lg font-semibold text-white">Все ваши карты</h2>
            <p className="text-sm text-arcane-300">
              всего: {ownCards?.length ?? myPlayer.hand.length + myPlayer.table.length + myPlayer.discard.length}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            {isLoadingOwnCards && (
              <p className="text-arcane-300">Загружаем карты...</p>
            )}
            {!isLoadingOwnCards && ownCards?.length === 0 && (
              <p className="text-arcane-300">Карты не найдены.</p>
            )}
            {ownCards?.map((card) => (
              <CardTile key={card.id} card={card} disabled />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
