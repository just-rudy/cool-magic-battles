export const ROLE_LABELS: Record<string, string> = {
  guest: 'Гость',
  authenticated: 'Пользователь',
  player: 'Игрок',
  moderator: 'Модератор',
  master: 'Мастер',
}

export function getRoleLabel(role: string): string {
  return ROLE_LABELS[role] ?? role
}

export function isMasterRole(role: string | undefined): boolean {
  return role === 'master'
}
