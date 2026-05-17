'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { LogOut, RefreshCw, Loader2 } from 'lucide-react'

import { useAuthStore } from '@/store/authStore'
import { listAllNotes, reindex } from '@/lib/knowledge'
import type { NoteAdmin } from '@/types/knowledge'

export default function AdminDashboardPage() {
  const [notes, setNotes] = useState<NoteAdmin[]>([])
  const [loading, setLoading] = useState(true)
  const [reindexing, setReindexing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const token = useAuthStore((s) => s.token)
  const signOut = useAuthStore((s) => s.signOut)
  const isAuthed = useAuthStore((s) => s.isAuthenticated())
  const router = useRouter()

  useEffect(() => {
    if (!isAuthed || !token) {
      router.replace('/knowledge/admin/login')
      return
    }
    listAllNotes(token)
      .then(setNotes)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [isAuthed, token, router])

  const doReindex = async () => {
    if (!token) return
    setReindexing(true)
    try {
      await reindex(token)
      const fresh = await listAllNotes(token)
      setNotes(fresh)
    } catch (err: any) {
      setError(err?.message ?? 'Reindex failed')
    } finally {
      setReindexing(false)
    }
  }

  if (!isAuthed) return null

  return (
    <main className="section-container pt-24">
      <header className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Knowledge Hub Admin</h1>
        <div className="flex items-center gap-2">
          <button
            onClick={doReindex}
            disabled={reindexing}
            className="btn-secondary flex items-center gap-2 disabled:opacity-60"
          >
            {reindexing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <RefreshCw className="w-4 h-4" />
            )}
            Reindex
          </button>
          <button
            onClick={() => {
              signOut()
              router.replace('/knowledge/admin/login')
            }}
            className="btn-secondary flex items-center gap-2"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </header>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
        </div>
      ) : error ? (
        <p className="text-red-600 dark:text-red-400">{error}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-200 dark:border-dark-border text-left">
                <th className="py-2 pr-4">Title</th>
                <th className="py-2 pr-4">Section</th>
                <th className="py-2 pr-4">Visibility</th>
                <th className="py-2 pr-4">Updated</th>
                <th className="py-2 pr-4"></th>
              </tr>
            </thead>
            <tbody>
              {notes.map((n) => (
                <tr
                  key={n.id}
                  className="border-b border-gray-100 dark:border-dark-border hover:bg-gray-50 dark:hover:bg-dark-card/50"
                >
                  <td className="py-3 pr-4 font-medium">{n.title}</td>
                  <td className="py-3 pr-4 text-gray-500">{n.section_slug}</td>
                  <td className="py-3 pr-4">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        n.visibility === 'public'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                      }`}
                    >
                      {n.visibility}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-gray-500">
                    {n.updated_at
                      ? new Date(n.updated_at).toLocaleDateString()
                      : '—'}
                  </td>
                  <td className="py-3 pr-4">
                    <Link
                      href={`/knowledge/admin/editor/${n.id}`}
                      className="text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}
