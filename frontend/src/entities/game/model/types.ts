export interface CardImage {
  id: string
  title: string
  file: string | null
  url: string | null
}

export interface Card {
  id: string
  title: string
  creature: string
  image_id: string
  image: CardImage | null
  power: number
  echo: number
  cost: number
  cool_points: number
}

export interface Player {
  id: string
  user_id: string
  nickname: string
  turn_order: number
  health: number
  base_echo: number
  cur_echo: number
  hand_size: number
  hand: Card[]
  table: Card[]
  discard: Card[]
  draw_count: number
  cool_points: number
  cards_count: number
}

export interface Winner {
  player_id: string
  nickname: string
  cool_points: number
  cards_count: number
}

export interface Game {
  id: string
  status: string
  cur_turn: number
  cur_player_id: string | null
  winner: Winner | null
  players: Player[]
  market: Card[]
  banish_count: number
  deck_count: number
}

export interface User {
  id: string
  username: string
}
