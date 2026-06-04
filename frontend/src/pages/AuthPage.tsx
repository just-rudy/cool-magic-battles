import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import axios from 'axios'
import { loginUser, registerUser } from '@/entities/user/api/userApi'
import { Layout } from '@/shared/ui/Layout'
import { useSessionStore } from '@/shared/store/sessionStore'

type AuthMode = 'login' | 'register'

export function AuthPage() {
  const navigate = useNavigate()
  const { userId, setUser } = useSessionStore()
  const [authMode, setAuthMode] = useState<AuthMode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [message, setMessage] = useState<string | null>(null)

  if (userId) {
    navigate('/profile', { replace: true })
    return null
  }

  const login = useMutation({
    mutationFn: () => loginUser({ username: username.trim(), password }),
    onSuccess: (user) => {
      setUser(user.id, user.username, user.role)
      navigate('/profile')
    },
    onError: (error) => setMessage(readError(error)),
  })

  const register = useMutation({
    mutationFn: () =>
      registerUser({
        username: username.trim(),
        password,
        password_confirm: passwordConfirm,
      }),
    onSuccess: (user) => {
      setUser(user.id, user.username, user.role)
      navigate('/profile')
    },
    onError: (error) => setMessage(readError(error)),
  })

  const busy = login.isPending || register.isPending

  const submit = () => {
    if (authMode === 'login') {
      login.mutate()
    } else {
      register.mutate()
    }
  }

  return (
    <Layout
      title="Вход в Крутые магические битвы"
      subtitle="Создайте аккаунт или войдите, чтобы играть онлайн."
    >
      <section className="mx-auto max-w-md rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
        <div className="mb-6 flex rounded-xl border border-arcane-500/40 p-1">
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

        <div className="space-y-4">
          <Field label="Имя мага (латиница, цифры, _)">
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={inputClass}
              placeholder="Gandalf"
              autoComplete="username"
            />
          </Field>

          <Field label="Пароль">
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputClass}
              placeholder="не менее 6 символов"
              autoComplete={
                authMode === 'login' ? 'current-password' : 'new-password'
              }
            />
          </Field>

          {authMode === 'register' && (
            <Field label="Повтор пароля">
              <input
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                className={inputClass}
                autoComplete="new-password"
              />
            </Field>
          )}

          <button
            type="button"
            disabled={busy || !username.trim() || !password}
            onClick={submit}
            className="w-full rounded-xl bg-arcane-500 px-4 py-3 font-semibold text-white hover:bg-arcane-400 disabled:opacity-50"
          >
            {authMode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </div>

        {message && (
          <p className="mt-4 rounded-lg border border-red-400/40 bg-red-950/40 px-3 py-2 text-sm text-red-200">
            {message}
          </p>
        )}

        <p className="mt-6 text-center text-sm text-arcane-300">
          Для теста в разных вкладках: войдите под разными аккаунтами в каждой
          вкладке браузера.
        </p>
      </section>
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

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm text-arcane-300">{label}</span>
      {children}
    </label>
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
