'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Loader2, Save, X } from 'lucide-react'

import { useAuthStore } from '@/store/authStore'
import { getAdminNote, updateAdminNote } from '@/lib/knowledge'
import type { NoteAdmin } from '@/types/knowledge'

export default function NoteEditorPage() {
  const params = useParams<{ id: string }>()
  const id = Number(params.id)
  const router = useRouter()
  const token = useAuthStore((s) => s.token)
  const isAuthed = useAuthStore((s) => s.isAuthenticated())

  const [note, setNote] = useState<NoteAdmin | null>(null)
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [visibility, setVisibility] = useState<'public' | 'draft'>('public')
  const [tagsText, setTagsText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthed || !token) {
      router.replace('/knowledge/admin/login')
      return
    }
    getAdminNote(id, token)
      .then((n) => {
        setNote(n)
        setTitle(n.title)
        setContent(n.content)
        setVisibility(n.visibility as 'public' | 'draft')
        setTagsText(n.tags.join(', '))
      })
      .catch((err) => setError(err.message))
  }, [id, isAuthed, token, router])

  const save = async () => {
    if (!token) return
    setBusy(true)
    setError(null)
    try {
      await updateAdminNote(
        id,
        {
          title,
          content,
          visibility,
          tags: tagsText
            .split(',')
            .map((t) => t.trim())
            .filter(Boolean),
        },
        token,
      )
      router.push('/knowledge/admin')
    } catch (err: any) {
      setError(err?.message ?? 'Save failed')
    } finally {
      setBusy(false)
    }
  }

  if (!isAuthed) return null
  if (!note && !error) {
    return (
      <main className="section-container pt-24 flex justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
      </main>
    )
  }

  return (
    <main className="section-container pt-24 max-w-5xl">
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Edit note</h1>
        <div className="flex gap-2">
          <button
            onClick={() => router.push('/knowledge/admin')}
            className="btn-secondary flex items-center gap-2"
          >
            <X className="w-4 h-4" /> Cancel
          </button>
          <button
            onClick={save}
            disabled={busy}
            className="btn-primary flex items-center gap-2 disabled:opacity-60"
          >
            {busy ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save
          </button>
        </div>
      </header>

      {error && (
        <p className="mb-4 text-sm text-red-600 dark:text-red-400">{error}</p>
      )}

      <div className="grid md:grid-cols-3 gap-4 mb-4">
        <input
          className="md:col-span-2 px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg text-lg font-semibold"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title"
        />
        <select
          className="px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg"
          value={visibility}
          onChange={(e) =>
            setVisibility(e.target.value as 'public' | 'draft')
          }
        >
          <option value="public">public</option>
          <option value="draft">draft</option>
        </select>
      </div>

      <input
        className="w-full mb-4 px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg"
        value={tagsText}
        onChange={(e) => setTagsText(e.target.value)}
        placeholder="comma, separated, tags"
      />

      <textarea
        className="w-full min-h-[60vh] px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg font-mono text-sm"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        spellCheck={false}
      />
    </main>
  )
}
