'use client'

import { motion, useInView } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { BookOpen, ArrowRight, Clock, Tag } from 'lucide-react'

import type { NoteCard as NoteCardType } from '@/types/knowledge'

// Home-page "Latest writing" section — surfaces the three most recently
// updated public notes from the knowledge hub rather than a hard-coded list.
// Falls back to a graceful empty state if the backend is unreachable.

interface Aggregate {
  notes: NoteCardType[]
  total: number
}

async function fetchRecent(): Promise<Aggregate> {
  const base = process.env.NEXT_PUBLIC_API_URL || ''
  const sections: { slug: string; note_count: number }[] = await fetch(
    `${base}/api/knowledge/sections`,
    { cache: 'no-store' },
  )
    .then((r) => (r.ok ? r.json() : []))
    .catch(() => [])

  const all: NoteCardType[] = []
  await Promise.all(
    sections.map(async (s) => {
      const payload = await fetch(
        `${base}/api/knowledge/sections/${s.slug}`,
        { cache: 'no-store' },
      )
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null)
      if (payload?.notes) all.push(...payload.notes)
    }),
  )

  all.sort((a, b) => {
    const av = a.updated_at ?? a.created_at
    const bv = b.updated_at ?? b.created_at
    return new Date(bv).getTime() - new Date(av).getTime()
  })

  return {
    notes: all.slice(0, 3),
    total: sections.reduce((n, s) => n + (s.note_count ?? 0), 0),
  }
}

export default function Blog() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })
  const [data, setData] = useState<Aggregate | null>(null)

  useEffect(() => {
    fetchRecent()
      .then(setData)
      .catch(() => setData({ notes: [], total: 0 }))
  }, [])

  return (
    <section id="blog" className="section-container" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          From the <span className="gradient-text">Knowledge Hub</span>
        </h2>
        <p className="text-center text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto">
          A live snapshot of my AI/ML knowledge base — {data?.total ?? 0}+ deep
          dives across transformers, RAG, computer vision, MLOps, and agentic
          systems.
        </p>
      </motion.div>

      {data === null ? (
        <div className="grid md:grid-cols-3 gap-6 animate-pulse">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card h-48" />
          ))}
        </div>
      ) : data.notes.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400">
          Knowledge hub is warming up.
        </div>
      ) : (
        <div className="grid md:grid-cols-3 gap-6">
          {data.notes.map((note, index) => (
            <motion.article
              key={note.id}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="card group cursor-pointer"
            >
              <div className="flex items-center gap-2 mb-4">
                <span className="skill-badge text-xs">
                  {note.section_slug}
                </span>
                {note.read_time > 0 && (
                  <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {note.read_time} min
                  </span>
                )}
              </div>
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {note.title}
              </h3>
              {note.summary && (
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
                  {note.summary}
                </p>
              )}
              {note.tags.length > 0 && (
                <div className="flex flex-wrap items-center gap-1 mt-3 text-xs text-gray-500 dark:text-gray-400">
                  <Tag className="w-3 h-3" />
                  {note.tags.slice(0, 3).map((t) => (
                    <span key={t}>#{t}</span>
                  ))}
                </div>
              )}
              <div className="mt-4 pt-4 border-t border-gray-100 dark:border-dark-border">
                <Link
                  href={`/knowledge/${note.section_slug}/${note.slug}`}
                  className="text-primary-600 dark:text-primary-400 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all"
                >
                  Read more <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </motion.article>
          ))}
        </div>
      )}

      <div className="mt-10 text-center">
        <Link
          href="/knowledge"
          className="btn-primary inline-flex items-center gap-2"
        >
          <BookOpen className="w-4 h-4" />
          Explore the full knowledge hub
        </Link>
      </div>
    </section>
  )
}
