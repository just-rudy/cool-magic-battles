import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  createGame,
  joinGame,
  joinGameByRef,
  listGames,
} from '@/entities/game/api/gameApi'
import { Layout } from '@/shared/ui/Layout'
import { useSessionStore } from '@/shared/store/sessionStore'
import { findPlayerByUserId } from '@/shared/lib/game'

const GAME_NAME_PATTERN = /^[A-Za-z0-9-]*$/

export function LobbyPage() {
  const navigate = useNavigate()
  const { userId, username, setGame } = useSessionStore()
  const [gameName, setGameName] = useState('')
  const [joinRef, setJoinRef] = useState('')
  const [selectedGameId, setSelectedGameId] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  const gamesQuery = useQuery({
    queryKey: ['games', 'lobby'],
    queryFn: listGames,
    refetchInterval: 5000,
  })

  const openGames = gamesQuery.data ?? []

  const create = useMutation({
    mutationFn: async () => {
      if (!userId) throw new Error('Сначала войдите в систему')
      const trimmed = gameName.trim()
      if (trimmed && !GAME_NAME_PATTERN.test(trimmed)) {
        throw new Error('Название: только латиница, цифры и дефис')
      }
      const game = await createGame(userId, trimmed || null)
      const joined = await joinGame(game.id, userId)
      const player = findPlayerByUserId(joined, userId)
      if (!player) throw new Error('Не удалось присоединиться к игре')
      return { game: joined, player }
    },
    onSuccess: ({ game, player }) => {
      setGame(game.id, player.id)
      navigate(`/game/${game.id}`)
    },
    onError: (error) => setMessage(readError(error)),
  })

  const join = useMutation({
    mutationFn: async () => {
      if (!userId) throw new Error('Сначала войдите в систему')
      const ref = selectedGameId || joinRef.trim()
      if (!ref) throw new Error('Укажите название игры или выберите из списка')
      const game = await joinGameByRef(ref, userId)
      const player = findPlayerByUserId(game, userId)
      if (!player) throw new Error('Не удалось присоединиться')
      return { game, player }
    },
    onSuccess: ({ game, player }) => {
      setGame(game.id, player.id)
      navigate(`/game/${game.id}`)
    },
    onError: (error) => setMessage(readError(error)),
  })

  const busy = create.isPending || join.isPending

  return (
    <Layout
      title="Лобби"
      subtitle={
        username
          ? `Добро пожаловать, ${username}. Создайте партию или присоединитесь.`
          : 'Создайте партию или присоединитесь.'
      }
    >
      <nav className="mb-6 flex flex-wrap gap-3 text-sm">
        <Link
          to="/profile"
          className="rounded-lg border border-arcane-500/40 px-3 py-1.5 text-arcane-300 hover:text-white"
        >
          Личный кабинет
        </Link>
      </nav>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Создать игру">
          <p className="mb-3 text-sm text-arcane-300">
            Название (латиница и цифры). Пустое поле — автоматически{' '}
            <code className="text-gold-400">game-123</code>.
          </p>
          <input
            value={gameName}
            onChange={(e) => setGameName(e.target.value)}
            className={inputClass}
            placeholder="my-battle"
            maxLength={50}
          />
          <button
            type="button"
            disabled={busy}
            onClick={() => create.mutate()}
            className="mt-4 w-full rounded-xl bg-gold-500 px-4 py-3 font-semibold text-arcane-950 hover:bg-gold-400 disabled:opacity-50"
          >
            Создать и войти
          </button>
        </Panel>

        <Panel title="Присоединиться">
          <label className="mb-2 block text-sm text-arcane-300">
            Название или UUID игры
          </label>
          <input
            value={joinRef}
            onChange={(e) => {
              setJoinRef(e.target.value)
              setSelectedGameId('')
            }}
            className={inputClass}
            placeholder="game-742 или uuid"
          />

          <label className="mb-2 mt-4 block text-sm text-arcane-300">
            Или выберите из списка
          </label>
          <select
            value={selectedGameId}
            onChange={(e) => {
              setSelectedGameId(e.target.value)
              const game = openGames.find((g) => g.id === e.target.value)
              if (game) setJoinRef(game.name)
            }}
            className={inputClass}
          >
            <option value="">— выберите игру —</option>
            {openGames.map((game) => (
              <option key={game.id} value={game.id}>
                {game.name} ({game.status}, игроков: {game.players_count})
              </option>
            ))}
          </select>

          {gamesQuery.isLoading && (
            <p className="mt-2 text-xs text-arcane-300">Обновление списка…</p>
          )}

          <button
            type="button"
            disabled={busy || (!joinRef.trim() && !selectedGameId)}
            onClick={() => join.mutate()}
            className="mt-4 w-full rounded-xl border border-arcane-400 px-4 py-3 font-semibold text-white hover:bg-arcane-700/50 disabled:opacity-50"
          >
            Присоединиться
          </button>
        </Panel>
      </div>

      {message && (
        <p className="mt-6 rounded-xl border border-arcane-500/30 bg-arcane-800/50 px-4 py-3 text-sm text-arcane-300">
          {message}
        </p>
      )}
    </Layout>
  )
}

function Panel({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
      <h2 className="mb-4 text-xl font-semibold text-white">{title}</h2>
      {children}
    </section>
  )
}

const inputClass =
  'w-full rounded-xl border border-arcane-500/40 bg-arcane-900 px-4 py-3 text-white outline-none focus:border-arcane-400'

function readError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
  }
  if (error instanceof Error) return error.message
  return 'Произошла ошибка'
}
