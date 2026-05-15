import type { Card } from '@/entities/game/model/types'

interface CardTileProps {
  card: Card
  onClick?: () => void
  disabled?: boolean
  highlight?: boolean
  compact?: boolean
}

export function CardTile({
  card,
  onClick,
  disabled = false,
  highlight = false,
  compact = false,
}: CardTileProps) {
  const interactive = Boolean(onClick) && !disabled

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!interactive}
      className={[
        'relative flex flex-col rounded-xl border text-left transition',
        compact ? 'min-w-[140px] p-3' : 'min-w-[170px] p-4',
        highlight
          ? 'border-gold-400 bg-arcane-700/90 shadow-[0_0_24px_rgba(255,213,79,0.35)]'
          : 'border-arcane-500/40 bg-arcane-800/80',
        interactive
          ? 'cursor-pointer hover:-translate-y-1 hover:border-arcane-400 hover:shadow-lg'
          : 'cursor-default opacity-70',
      ].join(' ')}
    >
      <span className="text-[10px] uppercase tracking-[0.2em] text-arcane-300">
        {card.creature}
      </span>
      <span className="mt-1 font-semibold text-white">{card.title}</span>
      <div
        className={[
          'mt-3 grid gap-1 text-xs text-arcane-300',
          compact ? 'grid-cols-2' : 'grid-cols-3',
        ].join(' ')}
      >
        <Stat label="Сила" value={card.power} />
        <Stat label="Эхо" value={card.echo} />
        <Stat label="Цена" value={card.cost} />
        {!compact && <Stat label="Крутость" value={card.cool_points} />}
      </div>
    </button>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <span className="block text-[10px] uppercase">{label}</span>
      <span className="font-semibold text-gold-400">{value}</span>
    </div>
  )
}
