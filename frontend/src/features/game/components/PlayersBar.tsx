import type { Game, Player } from '@/entities/game/model/types'

interface PlayersBarProps {
  game: Game
  myPlayerId: string | null
}

export function PlayersBar({ game, myPlayerId }: PlayersBarProps) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
      {game.players.map((player) => (
        <PlayerCard
          key={player.id}
          player={player}
          active={game.cur_player_id === player.id}
          isMe={player.id === myPlayerId}
          isWinner={game.winner?.player_id === player.id}
        />
      ))}
    </section>
  )
}

function PlayerCard({
  player,
  active,
  isMe,
  isWinner,
}: {
  player: Player
  active: boolean
  isMe: boolean
  isWinner: boolean
}) {
  return (
    <article
      className={[
        'rounded-2xl border p-4 backdrop-blur',
        isWinner
          ? 'border-emerald-400 bg-emerald-950/30'
          : active
            ? 'border-gold-400 bg-arcane-700/70'
            : 'border-arcane-500/30 bg-arcane-800/50',
      ].join(' ')}
    >
      <header className="flex items-center justify-between gap-2">
        <h3 className="text-lg font-semibold text-white">
          {player.nickname}
          {isMe && <span className="ml-2 text-xs text-gold-400">(вы)</span>}
        </h3>
        {active && (
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
