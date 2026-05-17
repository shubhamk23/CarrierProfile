'use client'

import { useRouter } from 'next/navigation'
import { useState, FormEvent } from 'react'
import { LogIn, Loader2 } from 'lucide-react'

import { useAuthStore } from '@/store/authStore'
import { login } from '@/lib/knowledge'

export default function AdminLoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const signIn = useAuthStore((s) => s.signIn)
  const router = useRouter()

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const res = await login(username, password)
      signIn(res.access_token, username, res.expires_in)
      router.replace('/knowledge/admin')
    } catch (err: any) {
      setError(err?.message ?? 'Sign-in failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="section-container pt-24 max-w-md">
      <h1 className="text-2xl font-bold mb-6 text-center">
        Knowledge Hub Admin
      </h1>
      <form onSubmit={submit} className="card space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full px-3 py-2 rounded-md border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg"
          />
        </div>
        {error && (
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        )}
        <button
          type="submit"
          disabled={busy}
          className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-60"
        >
          {busy ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <LogIn className="w-4 h-4" />
          )}
          Sign in
        </button>
      </form>
    </main>
  )
}
