import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import {
  createCatalogCard,
  deleteCatalogCard,
  listCardTypes,
  listCatalogCards,
  updateCatalogCard,
  type CardPayload,
} from '@/entities/card/api/cardApi'
import type { Card, CardType } from '@/entities/game/model/types'
import { Layout } from '@/shared/ui/Layout'
import { CardTile } from '@/shared/ui/CardTile'
import {
  getActionLabel,
  usagePatternLabels,
} from '@/shared/lib/cardEffects'

const emptyForm: CardPayload = {
  title: '',
  creature: '',
  card_type_id: '',
  power: 1,
  echo: 1,
  cost: 3,
  cool_points: 0,
}

function cardToForm(card: Card): CardPayload {
  return {
    title: card.title,
    creature: card.creature,
    card_type_id: card.card_type?.id ?? '',
    power: card.power,
    echo: card.echo,
    cost: card.cost,
    cool_points: card.cool_points,
  }
}

function formatCardTypeLabel(cardType: CardType): string {
  const usage =
    usagePatternLabels[cardType.usage_pattern] ?? cardType.usage_pattern
  return `${getActionLabel(cardType.action)} · ${usage}`
}

export function CatalogEditPage() {
  const queryClient = useQueryClient()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState<CardPayload>(emptyForm)
  const [message, setMessage] = useState<string | null>(null)

  const cardsQuery = useQuery({
    queryKey: ['catalog', 'cards'],
    queryFn: listCatalogCards,
  })

  const typesQuery = useQuery({
    queryKey: ['catalog', 'card-types'],
    queryFn: listCardTypes,
  })

  const cardTypes = typesQuery.data ?? []

  const defaultCardTypeId = useMemo(
    () => cardTypes[0]?.id ?? '',
    [cardTypes],
  )

  const save = useMutation({
    mutationFn: async () => {
      const payload = {
        ...form,
        card_type_id: form.card_type_id || defaultCardTypeId,
      }
      if (!payload.title.trim() || !payload.creature.trim()) {
        throw new Error('Заполните название и существо')
      }
      if (!payload.card_type_id) {
        throw new Error('Выберите тип карты')
      }
      if (editingId) {
        return updateCatalogCard(editingId, payload)
      }
      return createCatalogCard(payload)
    },
    onSuccess: async () => {
      setMessage(editingId ? 'Карта обновлена' : 'Карта добавлена')
      setEditingId(null)
      setForm({ ...emptyForm, card_type_id: defaultCardTypeId })
      await queryClient.invalidateQueries({ queryKey: ['catalog', 'cards'] })
    },
    onError: (error) => setMessage(readError(error)),
  })

  const remove = useMutation({
    mutationFn: deleteCatalogCard,
    onSuccess: async (_, cardId) => {
      setMessage('Карта удалена')
      if (editingId === cardId) {
        setEditingId(null)
        setForm({ ...emptyForm, card_type_id: defaultCardTypeId })
      }
      await queryClient.invalidateQueries({ queryKey: ['catalog', 'cards'] })
    },
    onError: (error) => setMessage(readError(error)),
  })

  const startCreate = () => {
    setEditingId(null)
    setForm({ ...emptyForm, card_type_id: defaultCardTypeId })
    setMessage(null)
  }

  const startEdit = (card: Card) => {
    setEditingId(card.id)
    setForm(cardToForm(card))
    setMessage(null)
  }

  const cards = cardsQuery.data ?? []

  return (
    <Layout
      title="Редактирование каталога"
      subtitle="Добавление, изменение и удаление карт в каталоге. Доступно только мастеру."
    >
      <div className="mb-6 flex flex-wrap gap-3">
        <Link
          to="/profile"
          className="rounded-xl border border-arcane-500/40 px-4 py-2 text-arcane-300 hover:text-white"
        >
          ← Профиль
        </Link>
        <button
          type="button"
          onClick={startCreate}
          className="rounded-xl bg-gold-500 px-4 py-2 font-semibold text-arcane-950 hover:bg-gold-400"
        >
          Новая карта
        </button>
      </div>

      {message && (
        <p className="mb-4 rounded-xl border border-arcane-500/30 bg-arcane-800/60 px-4 py-3 text-sm text-arcane-200">
          {message}
        </p>
      )}

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.2fr)]">
        <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">
            {editingId ? 'Редактировать карту' : 'Новая карта'}
          </h2>

          {typesQuery.isLoading && (
            <p className="text-arcane-300">Загрузка типов карт…</p>
          )}

          {typesQuery.isError && (
            <p className="text-red-300">Не удалось загрузить типы карт.</p>
          )}

          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault()
              save.mutate()
            }}
          >
            <Field label="Название">
              <input
                className={inputClass}
                value={form.title}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, title: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Существо">
              <input
                className={inputClass}
                value={form.creature}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, creature: e.target.value }))
                }
                required
              />
            </Field>
            <Field label="Тип карты">
              <select
                className={inputClass}
                value={form.card_type_id || defaultCardTypeId}
                onChange={(e) =>
                  setForm((prev) => ({
                    ...prev,
                    card_type_id: e.target.value,
                  }))
                }
                required
                disabled={cardTypes.length === 0}
              >
                {cardTypes.map((cardType) => (
                  <option key={cardType.id} value={cardType.id}>
                    {formatCardTypeLabel(cardType)}
                  </option>
                ))}
              </select>
            </Field>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Сила">
                <input
                  type="number"
                  min={0}
                  className={inputClass}
                  value={form.power}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      power: Number(e.target.value),
                    }))
                  }
                />
              </Field>
              <Field label="Эхо">
                <input
                  type="number"
                  min={0}
                  className={inputClass}
                  value={form.echo}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      echo: Number(e.target.value),
                    }))
                  }
                />
              </Field>
              <Field label="Цена">
                <input
                  type="number"
                  min={0}
                  className={inputClass}
                  value={form.cost}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      cost: Number(e.target.value),
                    }))
                  }
                />
              </Field>
              <Field label="Крутость">
                <input
                  type="number"
                  min={0}
                  className={inputClass}
                  value={form.cool_points}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      cool_points: Number(e.target.value),
                    }))
                  }
                />
              </Field>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <button
                type="submit"
                disabled={save.isPending || cardTypes.length === 0}
                className="rounded-xl bg-gold-500 px-4 py-2 font-semibold text-arcane-950 hover:bg-gold-400 disabled:opacity-50"
              >
                {save.isPending
                  ? 'Сохранение…'
                  : editingId
                    ? 'Сохранить'
                    : 'Добавить'}
              </button>
              {editingId && (
                <button
                  type="button"
                  onClick={startCreate}
                  className="rounded-xl border border-arcane-500/40 px-4 py-2 text-arcane-300 hover:text-white"
                >
                  Отмена
                </button>
              )}
            </div>
          </form>
        </section>

        <section className="rounded-2xl border border-arcane-500/30 bg-arcane-800/40 p-6">
          <h2 className="mb-4 text-xl font-semibold text-white">
            Каталог ({cards.length})
          </h2>

          {cardsQuery.isLoading && (
            <p className="text-arcane-300">Загрузка карт…</p>
          )}

          {cardsQuery.isError && (
            <p className="text-red-300">Не удалось загрузить каталог.</p>
          )}

          <ul className="space-y-4">
            {cards.map((card) => (
              <li
                key={card.id}
                className="rounded-xl border border-arcane-500/20 bg-arcane-900/40 p-4"
              >
                <div className="mb-3 max-w-xs">
                  <CardTile card={card} compact disabled />
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => startEdit(card)}
                    className="rounded-lg border border-arcane-500/40 px-3 py-1.5 text-sm text-arcane-200 hover:text-white"
                  >
                    Редактировать
                  </button>
                  <button
                    type="button"
                    disabled={remove.isPending}
                    onClick={() => {
                      if (
                        window.confirm(
                          `Удалить карту «${card.title}» из каталога?`,
                        )
                      ) {
                        remove.mutate(card.id)
                      }
                    }}
                    className="rounded-lg border border-red-500/40 px-3 py-1.5 text-sm text-red-300 hover:text-red-200"
                  >
                    Удалить
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </Layout>
  )
}

const inputClass =
  'w-full rounded-lg border border-arcane-500/30 bg-arcane-900/60 px-3 py-2 text-white outline-none focus:border-gold-500/50'

function Field({
  label,
  children,
}: {
  label: string
  children: React.ReactNode
}) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-arcane-300">{label}</span>
      {children}
    </label>
  )
}

function readError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg ?? String(item)).join('; ')
    }
  }
  if (error instanceof Error) return error.message
  return 'Ошибка операции'
}
