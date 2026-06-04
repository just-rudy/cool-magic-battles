import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Layout } from '@/shared/ui/Layout'
import { useSessionStore } from '@/shared/store/sessionStore'
import { useGame } from '@/features/game/hooks/useGame'
import { GameBoard } from '@/features/game/components/GameBoard'
import { findPlayerByUserId } from '@/shared/lib/game'

export function GamePage() {
  const { gameId } = useParams<{ gameId: string }>()
  const { userId, playerId, setGame } = useSessionStore()
  const { data: game, isLoading, error, refetch } = useGame(gameId ?? null)

  const myPlayer = game
    ? (game.players.find((player) => player.id === playerId) ??
      findPlayerByUserId(game, userId ?? ''))
    : undefined

  useEffect(() => {
    if (game && myPlayer && myPlayer.id !== playerId) {
      setGame(game.id, myPlayer.id)
    }
  }, [game, myPlayer, playerId, setGame])

  if (!gameId) {
    return (
      <Layout title="Игра не найдена">
        <p className="text-arcane-300">Некорректный адрес игры.</p>
      </Layout>
    )
  }

  if (!userId) {
    return (
      <Layout title="Нужен вход">
        <p className="text-arcane-300">
          <Link to="/auth" className="text-gold-400 hover:underline">
            Войдите в систему
          </Link>
          , чтобы играть.
        </p>
      </Layout>
    )
  }

  if (isLoading) {
    return (
      <Layout title="Загрузка игры">
        <p className="text-arcane-300">Подготавливаем поле боя…</p>
      </Layout>
    )
  }

  if (error || !game) {
    return (
      <Layout title="Ошибка">
        <p className="text-arcane-300">Не удалось загрузить игру.</p>
        <button
          type="button"
          onClick={() => refetch()}
          className="mt-4 rounded-xl bg-arcane-500 px-4 py-2 text-white"
        >
          Повторить
        </button>
      </Layout>
    )
  }

  if (!myPlayer) {
    return (
      <Layout title="Вы не в этой игре">
        <p className="text-arcane-300">
          Присоединитесь к игре из{' '}
          <Link to="/" className="text-gold-400 hover:underline">
            лобби
          </Link>
          .
        </p>
      </Layout>
    )
  }

  return (
    <Layout
      title={game.name || `Партия ${game.id.slice(0, 8)}…`}
      subtitle="Разыгрывайте карты, покупайте из рынка и завершайте ход, когда готовы."
    >
      <GameBoard game={game} myPlayer={myPlayer} />
    </Layout>
  )
}
