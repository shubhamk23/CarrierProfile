'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowRight, BookOpen } from 'lucide-react'

import type { Section } from '@/types/knowledge'

interface Props {
  section: Section
  index?: number
}

export default function SectionCard({ section, index = 0 }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
    >
      <Link
        href={`/knowledge/${section.slug}`}
        className="card group cursor-pointer block h-full"
      >
        <div className="flex items-start gap-3 mb-4">
          <span className="text-3xl">{section.icon ?? '📚'}</span>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {section.title}
            </h3>
            <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-1">
              <BookOpen className="w-3 h-3" />
              {section.note_count} {section.note_count === 1 ? 'note' : 'notes'}
            </span>
          </div>
        </div>
        {section.description && (
          <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3 mb-4">
            {section.description}
          </p>
        )}
        <div className="mt-auto pt-4 border-t border-gray-100 dark:border-dark-border">
          <span className="text-primary-600 dark:text-primary-400 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
            Explore <ArrowRight className="w-4 h-4" />
          </span>
        </div>
      </Link>
    </motion.div>
  )
}
