import type { Card } from '@/entities/game/model/types'

export const actionLabels: Record<string, string> = {
    attack: 'Атака',
    defense: 'Защита',
    draw: 'Добор',
    heal: 'Лечение',
    hand_buff: 'Увеличение руки',
    echo_buff: 'Увеличение эхо',
}

export const actionIcons: Record<string, string> = {
    attack: '⚔️',
    defense: '🛡️',
    draw: '🎴',
    heal: '💚',
    hand_buff: '🤲',
    echo_buff: '✨',
}

export const actionColors: Record<string, string> = {
    attack: 'text-red-400',
    defense: 'text-blue-400',
    draw: 'text-purple-400',
    heal: 'text-green-400',
    hand_buff: 'text-yellow-400',
    echo_buff: 'text-pink-400',
}

export const usagePatternLabels: Record<string, string> = {
    reg: 'Обычная',
    discard: 'Сброс',
    banish: 'Изгнание',
    on_top: 'На верх колоды',
}

export function getCardEffectDescription(card: Card): string {
    if (!card.card_type) {
        return 'Неизвестный эффект'
    }

    const action = card.card_type.action
    const power = card.power
    const echo = card.echo

    const descriptions: Record<string, string> = {
        attack: `Наносит ${power} урона цели`,
        defense: `Блокирует ${power} урона`,
        draw: `Добирает ${power} карт(ы)`,
        heal: `Восстанавливает ${power} здоровья цели (макс. 25)`,
        hand_buff: `Увеличивает размер руки на ${power}`,
        echo_buff: `Увеличивает базовое эхо на ${power}`,
    }

    const baseDesc = descriptions[action] || 'Неизвестный эффект'
    const echoDesc = echo > 0 ? ` • Даёт ${echo} эхо` : ''
    const usagePattern = card.card_type.usage_pattern
    const usageDesc =
        usagePattern !== 'reg' ? ` • ${usagePatternLabels[usagePattern]}` : ''

    return `${baseDesc}${echoDesc}${usageDesc}`
}

export function getActionLabel(action: string): string {
    return actionLabels[action] || action
}

export function getActionIcon(action: string): string {
    return actionIcons[action] || '❓'
}

export function getActionColor(action: string): string {
    return actionColors[action] || 'text-gray-400'
}
