import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { createGame, joinGame } from '@/entities/game/api/gameApi'
import { listUsers, loginUser, registerUser } from '@/entities/user/api/userApi'
import { Layout } from '@/shared/ui/Layout'
import { useSessionStore } from '@/shared/store/sessionStore'
import { findPlayerByUserId } from '@/shared/lib/game'
import type { User } from '@/entities/game/model/types'

type AuthMode = 'login' | 'register'

export function HomePage() {
  const navigate = useNavigate()
  const { userId, username, setUser, setGame, logout } = useSessionStore()
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [nameInput, setNameInput] = useState(username ?? '')
  const [joinGameId, setJoinGameId] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: listUsers,
    enabled: !userId,
  })

  const handleAuthSuccess = (user: User, isLogin: boolean) => {
    setUser(user.id, user.username)
    setMessage(
      isLogin
        ? `С возвращением, ${user.username}!`
        : `Аккаунт создан. Добро пожаловать, ${user.username}!`,
    )
  }

  const login = useMutation({
    mutationFn: () => loginUser(nameInput.trim()),
    onSuccess: (user) => handleAuthSuccess(user, true),
    onError: (error) => setMessage(readError(error)),
  })

  const register = useMutation({
    mutationFn: () => registerUser(nameInput.trim()),
    onSuccess: (user) => handleAuthSuccess(user, false),
    onError: (error) => setMessage(readError(error)),
  })

  const create = useMutation({
    mutationFn: async () => {
      if (!userId) throw new Error('Сначала войдите в систему')
      const game = await createGame(userId)
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
      const game = await joinGame(joinGameId.trim(), userId)
      const player = findPlayerByUserId(game, userId)
      if (!player) throw new Error('Не удалось присоединиться к игре')
      return { game, player }
    },
    onSuccess: ({ game, player }) => {
      setGame(game.id, player.id)
      navigate(`/game/${game.id}`)
    },
    onError: (error) => setMessage(readError(error)),
  })

  const busy =
    login.isPending || register.isPending || create.isPending || join.isPending

  const submitAuth = () => {
    if (authMode === 'login') {
      login.mutate()
    } else {
      register.mutate()
    }
  }

  const pickUser = (user: User) => {
    setNameInput(user.username)
    setUser(user.id, user.username)
    setMessage(`Вы вошли как ${user.username}`)
  }

  return (
    <Layout
      title="Лобби магов"
      subtitle="Войдите в аккаунт или зарегистрируйтесь, затем создайте партию или присоединитесь по ID."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Аккаунт">
          {userId ? (
            <div className="space-y-3">
              <p className="text-arcane-300">
                Вы вошли как{' '}
                <span className="font-semibold text-white">{username}</span>
              </p>
              <p className="break-all text-xs text-arcane-300">ID: {userId}</p>
              <button
                type="button"
                onClick={logout}
                className="rounded-lg border border-arcane-500/40 px-4 py-2 text-sm text-arcane-300 hover:border-arcane-400 hover:text-white"
              >
                Выйти
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex rounded-xl border border-arcane-500/40 p-1">
                <AuthTab
                  active={authMode === 'login'}
                  onClick={() => setAuthMode('login')}
                  label="Вход"
                />
                <AuthTab
                  active={authMode === 'register'}
                  onClick={() => setAuthMode('register')}
                  label="Регистрация"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm text-arcane-300" htmlFor="username">
                  Имя мага
                </label>
                <input
                  id="username"
                  value={nameInput}
                  onChange={(event) => setNameInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && nameInput.trim()) {
                      submitAuth()
                    }
                  }}
                  className="w-full rounded-xl border border-arcane-500/40 bg-arcane-900 px-4 py-3 text-white outline-none focus:border-arcane-400"
                  placeholder={
                    authMode === 'login' ? 'Введите имя' : 'Придумайте имя'
                  }
                />
              </div>

              <button
                type="button"
                disabled={busy || !nameInput.trim()}
                onClick={submitAuth}
                className="w-full rounded-xl bg-arcane-500 px-4 py-3 font-semibold text-white hover:bg-arcane-400 disabled:opacity-50"
              >
                {authMode === 'login' ? 'Войти' : 'Зарегистрироваться'}
              </button>

              {authMode === 'login' && (
                <ExistingUsersList
                  users={usersQuery.data ?? []}
                  loading={usersQuery.isLoading}
                  error={usersQuery.isError}
                  onPick={pickUser}
                  disabled={busy}
                />
              )}
            </div>
          )}
        </Panel>

        <Panel title="Игра">
          <div className="space-y-4">
            <button
              type="button"
              disabled={!userId || busy}
              onClick={() => create.mutate()}
              className="w-full rounded-xl bg-gold-500 px-4 py-3 font-semibold text-arcane-950 hover:bg-gold-400 disabled:opacity-50"
            >
              Создать новую игру
            </button>

            <div>
              <label className="mb-2 block text-sm text-arcane-300" htmlFor="game-id">
                ID существующей игры
              </label>
              <input
                id="game-id"
                value={joinGameId}
                onChange={(event) => setJoinGameId(event.target.value)}
                className="w-full rounded-xl border border-arcane-500/40 bg-arcane-900 px-4 py-3 text-white outline-none focus:border-arcane-400"
                placeholder="uuid игры"
              />
            </div>
            <button
              type="button"
              disabled={!userId || busy || !joinGameId.trim()}
              onClick={() => join.mutate()}
              className="w-full rounded-xl border border-arcane-400 px-4 py-3 font-semibold text-white hover:bg-arcane-700/50 disabled:opacity-50"
            >
              Присоединиться
            </button>
          </div>
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

function AuthTab({
  active,
  onClick,
  label,
}: {
  active: boolean
  onClick: () => void
  label: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'flex-1 rounded-lg px-3 py-2 text-sm font-semibold transition',
        active
          ? 'bg-arcane-500 text-white'
          : 'text-arcane-300 hover:text-white',
      ].join(' ')}
    >
      {label}
    </button>
  )
}

function ExistingUsersList({
  users,
  loading,
  error,
  onPick,
  disabled,
}: {
  users: User[]
  loading: boolean
  error: boolean
  onPick: (user: User) => void
  disabled: boolean
}) {
  if (loading) {
    return <p className="text-sm text-arcane-300">Загрузка списка магов…</p>
  }

  if (error) {
    return (
      <p className="text-sm text-arcane-300">
        Не удалось загрузить список. Введите имя вручную.
      </p>
    )
  }

  if (users.length === 0) {
    return (
      <p className="text-sm text-arcane-300">
        Пока нет зарегистрированных магов — создайте аккаунт во вкладке «Регистрация».
      </p>
    )
  }

  return (
    <div>
      <p className="mb-2 text-sm text-arcane-300">Или выберите из списка:</p>
      <ul className="max-h-40 space-y-1 overflow-y-auto rounded-xl border border-arcane-500/30 p-2">
        {users.map((user) => (
          <li key={user.id}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onPick(user)}
              className="w-full rounded-lg px-3 py-2 text-left text-sm text-white transition hover:bg-arcane-700/60 disabled:opacity-50"
            >
              {user.username}
            </button>
          </li>
        ))}
      </ul>
    </div>
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

function readError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg ?? String(item)).join(', ')
    }
  }
  if (error instanceof Error) return error.message
  return 'Произошла ошибка'
}
