'use client'

import type { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Calendar, Clock } from 'lucide-react'
import Link from 'next/link'
import type { BlogPost } from '@/lib/blog-posts'
import { formatBlogDate } from '@/lib/blog-posts'

function renderContent(content: string) {
  const lines = content.split('\n')
  const blocks: ReactNode[] = []
  let listBuffer: { type: 'ul' | 'ol'; items: string[] } | null = null

  const flushList = (key: string) => {
    if (!listBuffer) return
    const Tag = listBuffer.type
    blocks.push(
      <Tag key={`${key}-list`} className={Tag === 'ul' ? 'list-disc pl-6 mb-4' : 'list-decimal pl-6 mb-4'}>
        {listBuffer.items.map((item, i) => (
          <li key={i} className="mb-1 text-gray-700 dark:text-gray-300">
            {item}
          </li>
        ))}
      </Tag>
    )
    listBuffer = null
  }

  lines.forEach((line, index) => {
    const key = `line-${index}`

    if (line.startsWith('- ')) {
      if (listBuffer?.type !== 'ul') {
        flushList(key)
        listBuffer = { type: 'ul', items: [] }
      }
      listBuffer.items.push(line.replace('- ', ''))
      return
    }

    if (line.match(/^\d+\. /)) {
      if (listBuffer?.type !== 'ol') {
        flushList(key)
        listBuffer = { type: 'ol', items: [] }
      }
      listBuffer.items.push(line.replace(/^\d+\. /, ''))
      return
    }

    flushList(key)

    if (line.startsWith('# ')) {
      blocks.push(
        <h1 key={key} className="text-3xl font-bold mt-8 mb-4">
          {line.replace('# ', '')}
        </h1>
      )
    } else if (line.startsWith('## ')) {
      blocks.push(
        <h2 key={key} className="text-2xl font-bold mt-8 mb-4">
          {line.replace('## ', '')}
        </h2>
      )
    } else if (line.startsWith('### ')) {
      blocks.push(
        <h3 key={key} className="text-xl font-bold mt-6 mb-3">
          {line.replace('### ', '')}
        </h3>
      )
    } else if (line.startsWith('```')) {
      // fenced code markers are not rendered by this lightweight parser
    } else if (line.trim() === '') {
      blocks.push(<br key={key} />)
    } else {
      blocks.push(
        <p key={key} className="mb-4 text-gray-700 dark:text-gray-300">
          {line}
        </p>
      )
    }
  })

  flushList('trailing-list')

  return blocks
}

export default function PostContent({ post }: { post: BlogPost }) {
  return (
    <article className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Link
          href="/#blog"
          className="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:underline mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Blog
        </Link>

        <header className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <span className="skill-badge">{post.category}</span>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {post.title}
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">{post.excerpt}</p>
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              {formatBlogDate(post.date)}
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {post.readTime}
            </span>
          </div>
        </header>

        <div className="prose prose-lg dark:prose-invert max-w-none">{renderContent(post.content)}</div>
      </motion.div>
    </article>
  )
}
