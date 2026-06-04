import type { Card } from '@/entities/game/model/types'

export function cardNeedsTarget(card: Card): boolean {
  const action = card.card_type?.action
  return action === 'attack' || action === 'heal'
}

export function isDefenseCard(card: Card): boolean {
  return card.card_type?.action === 'defense'
}

export function canTargetPlayer(
  card: Card,
  targetPlayerId: string,
  myPlayerId: string,
): boolean {
  const action = card.card_type?.action
  if (action === 'attack') {
    return targetPlayerId !== myPlayerId
  }
  if (action === 'heal') {
    return true
  }
  return false
}

export function targetSelectionHint(card: Card): string {
  const action = card.card_type?.action
  if (action === 'attack') {
    return 'Выберите игрока для атаки'
  }
  if (action === 'heal') {
    return 'Выберите игрока для лечения'
  }
  return 'Выберите цель'
}
