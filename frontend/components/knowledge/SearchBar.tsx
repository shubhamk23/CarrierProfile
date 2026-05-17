'use client'

import { Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState, FormEvent } from 'react'

interface Props {
  initialQuery?: string
  autoFocus?: boolean
}

export default function SearchBar({ initialQuery = '', autoFocus }: Props) {
  const [q, setQ] = useState(initialQuery)
  const router = useRouter()

  const submit = (e: FormEvent) => {
    e.preventDefault()
    const trimmed = q.trim()
    if (!trimmed) return
    router.push(`/knowledge/search?q=${encodeURIComponent(trimmed)}`)
  }

  return (
    <form onSubmit={submit} className="relative max-w-2xl mx-auto">
      <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
      <input
        autoFocus={autoFocus}
        type="search"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search transformers, RAG, YOLO, RLHF…"
        className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-card text-gray-900 dark:text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
      />
    </form>
  )
}
