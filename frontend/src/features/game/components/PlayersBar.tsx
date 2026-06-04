import type { Card, Game, Player } from '@/entities/game/model/types'
import { canTargetPlayer } from '@/shared/lib/cardPlay'

interface PlayersBarProps {
  game: Game
  myPlayerId: string | null
  targetCard?: Card | null
  onSelectTarget?: (playerId: string) => void
  pending?: boolean
}

export function PlayersBar({
  game,
  myPlayerId,
  targetCard = null,
  onSelectTarget,
  pending = false,
}: PlayersBarProps) {
  const selecting = Boolean(targetCard && onSelectTarget)

  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {game.players.map((player) => {
        const isValid = Boolean(
          selecting &&
            myPlayerId &&
            targetCard &&
            canTargetPlayer(targetCard, player.id, myPlayerId),
        )

        return (
          <PlayerCard
            key={player.id}
            player={player}
            active={game.cur_player_id === player.id}
            isMe={player.id === myPlayerId}
            isWinner={game.winner?.player_id === player.id}
            isAttackTarget={game.pending_attack?.defender_id === player.id}
            selectable={isValid}
            disabled={selecting && !isValid}
            pending={pending}
            onSelect={isValid ? () => onSelectTarget?.(player.id) : undefined}
          />
        )
      })}
    </section>
  )
}

function PlayerCard({
  player,
  active,
  isMe,
  isWinner,
  isAttackTarget,
  selectable,
  disabled,
  pending,
  onSelect,
}: {
  player: Player
  active: boolean
  isMe: boolean
  isWinner: boolean
  isAttackTarget?: boolean
  selectable?: boolean
  disabled?: boolean
  pending?: boolean
  onSelect?: () => void
}) {
  const interactive = Boolean(onSelect) && !pending

  return (
    <article
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={interactive ? onSelect : undefined}
      onKeyDown={
        interactive
          ? (event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                onSelect?.()
              }
            }
          : undefined
      }
      className={[
        'rounded-2xl border p-4 backdrop-blur transition',
        selectable
          ? 'cursor-pointer border-cyan-400/60 bg-cyan-950/30 hover:border-cyan-300 hover:shadow-[0_0_20px_rgba(34,211,238,0.25)]'
          : disabled
            ? 'cursor-not-allowed opacity-50'
            : '',
        isWinner
          ? 'border-emerald-400 bg-emerald-950/30'
          : isAttackTarget
            ? 'border-red-400/60 bg-red-950/30'
            : active
              ? 'border-gold-400 bg-arcane-700/70'
              : !selectable && !disabled
                ? 'border-arcane-500/30 bg-arcane-800/50'
                : '',
      ].join(' ')}
    >
      <header className="flex items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-white">
          {player.nickname}
          {isMe && <span className="ml-2 text-xs text-gold-400">(вы)</span>}
        </h3>
        {selectable && (
          <span className="rounded-full bg-cyan-500/20 px-2 py-1 text-xs text-cyan-300">
            цель
          </span>
        )}
        {isAttackTarget && !selectable && (
          <span className="rounded-full bg-red-500/20 px-2 py-1 text-xs text-red-300">
            под атакой
          </span>
        )}
        {active && !selectable && (
          <span className="rounded-full bg-gold-500/20 px-2 py-1 text-xs text-gold-400">
            ход
          </span>
        )}
        {!active && isWinner && (
          <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300">
            победитель
          </span>
        )}
      </header>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-sm text-arcane-300">
        <Stat label="ОЗ" value={player.health} />
        <Stat label="Эхо" value={player.cur_echo} />
        <Stat label="База эхо" value={player.base_echo} />
        <Stat label="Рука" value={player.hand.length} />
        <Stat label="Крутость" value={player.cool_points} />
        <Stat label="Всего карт" value={player.cards_count} />
      </dl>
    </article>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <dt className="text-[10px] uppercase tracking-wide">{label}</dt>
      <dd className="font-semibold text-white">{value}</dd>
    </div>
  )
}
