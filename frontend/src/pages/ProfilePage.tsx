import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getCurrentUser } from '@/entities/user/api/userApi'
import { Layout } from '@/shared/ui/Layout'
import { getRoleLabel, isMasterRole } from '@/shared/lib/roles'
import { useSessionStore } from '@/shared/store/sessionStore'

export function ProfilePage() {
  const { username, logout } = useSessionStore()

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: getCurrentUser,
  })

  const profile = profileQuery.data

  return (
    <Layout
      title="Личный кабинет"
      subtitle="Ваш профиль и быстрый доступ к играм."
    >
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">Профиль</h2>

          {profileQuery.isLoading && (
            <p className="text-arcane-300">Загрузка…</p>
          )}

          {profileQuery.isError && (
            <p className="text-red-300">Не удалось загрузить профиль.</p>
          )}

          {profile && (
            <dl className="space-y-3 text-sm">
              <Row label="Имя" value={profile.username} />
              <Row label="Роль" value={getRoleLabel(profile.role)} />
              <Row label="ID" value={profile.id} mono />
              <Row
                label="Пароль"
                value={profile.has_password ? 'установлен' : 'не задан'}
              />
            </dl>
          )}

          {!profile && username && (
            <p className="text-white">
              Вы вошли как <strong>{username}</strong>
            </p>
          )}

          <div className="mt-6 flex flex-wrap gap-3">
            {profile && isMasterRole(profile.role) && (
              <Link
                to="/catalog/edit"
                className="rounded-xl border border-gold-500/50 bg-gold-500/10 px-4 py-2 font-semibold text-gold-300 hover:bg-gold-500/20"
              >
                Редактирование каталога
              </Link>
            )}
            <Link
              to="/"
              className="rounded-xl bg-gold-500 px-4 py-2 font-semibold text-arcane-950 hover:bg-gold-400"
            >
              В лобби
            </Link>
            <button
              type="button"
              onClick={logout}
              className="rounded-xl border border-arcane-500/40 px-4 py-2 text-arcane-300 hover:text-white"
            >
              Выйти
            </button>
          </div>
        </section>

        <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">
            Как играть вдвоём
          </h2>
          <ol className="list-decimal space-y-2 pl-5 text-sm text-arcane-300">
            <li>Войдите под первым магом (эта вкладка).</li>
            <li>
              Откройте{' '}
              <Link to="/auth" className="text-gold-400 hover:underline">
                /auth
              </Link>{' '}
              в режиме инкогнито или другом браузере.
            </li>
            <li>Зарегистрируйте второго мага и войдите.</li>
            <li>Один создаёт игру с названием, второй присоединяется по имени.</li>
            <li>Начните партию и ходите по очереди.</li>
          </ol>
        </section>
      </div>
    </Layout>
  )
}

function Row({
  label,
  value,
  mono = false,
}: {
  label: string
  value: string
  mono?: boolean
}) {
  return (
    <div>
      <dt className="text-arcane-300">{label}</dt>
      <dd
        className={[
          'font-medium text-white',
          mono ? 'break-all font-mono text-xs' : '',
        ].join(' ')}
      >
        {value}
      </dd>
    </div>
  )
}
