'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { Clock, Tag } from 'lucide-react'

import type { NoteCard as NoteCardType } from '@/types/knowledge'

interface Props {
  note: NoteCardType
  index?: number
}

const LEVEL_BADGE: Record<NoteCardType['level'], string> = {
  beginner:
    'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  intermediate:
    'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  advanced: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
}

export default function NoteCard({ note, index = 0 }: Props) {
  return (
    <motion.article
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
    >
      <Link
        href={`/knowledge/${note.section_slug}/${note.slug}`}
        className="card group cursor-pointer block h-full"
      >
        <div className="flex items-center gap-2 mb-3">
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${LEVEL_BADGE[note.level]}`}
          >
            {note.level}
          </span>
          {note.read_time > 0 && (
            <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {note.read_time} min read
            </span>
          )}
        </div>
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          {note.title}
        </h3>
        {note.summary && (
          <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
            {note.summary}
          </p>
        )}
        {note.tags.length > 0 && (
          <div className="flex flex-wrap items-center gap-1 mt-4 pt-4 border-t border-gray-100 dark:border-dark-border">
            <Tag className="w-3 h-3 text-gray-400" />
            {note.tags.slice(0, 4).map((tag) => (
              <span
                key={tag}
                className="text-xs text-gray-500 dark:text-gray-400"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}
      </Link>
    </motion.article>
  )
}
