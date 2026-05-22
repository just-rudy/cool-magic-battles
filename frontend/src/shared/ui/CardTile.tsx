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
  const imageUrl = card.image?.url
  const imageLabel = card.image?.title || card.title

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
      <div
        className={[
          'relative overflow-hidden rounded-lg border border-white/10 bg-arcane-950/80',
          compact ? 'h-28' : 'h-40',
        ].join(' ')}
      >
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={imageLabel}
            loading="lazy"
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-[radial-gradient(circle_at_top,_rgba(179,136,255,0.28),_transparent_58%),linear-gradient(180deg,_rgba(31,17,64,0.96),_rgba(11,6,24,0.96))] px-3 text-center">
            <span className="text-[11px] uppercase tracking-[0.28em] text-arcane-300">
              {card.creature}
            </span>
          </div>
        )}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-arcane-950 via-arcane-950/70 to-transparent px-3 pb-2 pt-6">
          <span className="line-clamp-2 text-sm font-semibold text-white">
            {card.title}
          </span>
        </div>
      </div>
      <span className="text-[10px] uppercase tracking-[0.2em] text-arcane-300">
        {card.creature}
      </span>
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
