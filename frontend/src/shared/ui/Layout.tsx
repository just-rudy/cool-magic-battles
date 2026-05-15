import { Link } from 'react-router-dom'

interface LayoutProps {
  title: string
  subtitle?: string
  children: React.ReactNode
}

export function Layout({ title, subtitle, children }: LayoutProps) {
  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-8">
      <header className="mb-8">
        <Link
          to="/"
          className="text-sm uppercase tracking-[0.35em] text-arcane-300 hover:text-white"
        >
          Крутые магические битвы
        </Link>
        <h1 className="mt-2 text-3xl font-bold text-white md:text-4xl">{title}</h1>
        {subtitle && <p className="mt-2 max-w-2xl text-arcane-300">{subtitle}</p>}
      </header>
      <main className="flex-1">{children}</main>
    </div>
  )
}
