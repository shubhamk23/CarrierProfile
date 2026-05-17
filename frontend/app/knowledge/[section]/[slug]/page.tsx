import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ChevronLeft, Clock, Tag } from 'lucide-react'

import NoteRenderer from '@/components/knowledge/NoteRenderer'
import { KnowledgeApiError, getNote } from '@/lib/knowledge'

interface PageProps {
  params: { section: string; slug: string }
}

export const revalidate = 60

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  try {
    const note = await getNote(params.section, params.slug)
    return {
      title: `${note.title} — Knowledge Hub`,
      description: note.summary ?? note.title,
      keywords: note.tags,
      openGraph: {
        title: note.title,
        description: note.summary ?? undefined,
        type: 'article',
        publishedTime: note.created_at,
        modifiedTime: note.updated_at ?? note.created_at,
        tags: note.tags,
      },
    }
  } catch {
    return { title: 'Note not found — Knowledge Hub' }
  }
}

export default async function NoteDetailPage({ params }: PageProps) {
  let note
  try {
    note = await getNote(params.section, params.slug)
  } catch (err) {
    if (err instanceof KnowledgeApiError && err.status === 404) {
      notFound()
    }
    throw err
  }

  // JSON-LD Article schema for SEO.
  const articleLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: note.title,
    description: note.summary ?? undefined,
    keywords: note.tags.join(', '),
    datePublished: note.created_at,
    dateModified: note.updated_at ?? note.created_at,
    author: { '@type': 'Person', name: 'Shubham Khanapure' },
  }

  return (
    <main className="section-container pt-24 max-w-4xl">
      <Link
        href={`/knowledge/${params.section}`}
        className="inline-flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline mb-6"
      >
        <ChevronLeft className="w-4 h-4" /> Back to section
      </Link>

      <article>
        <header className="mb-8 pb-8 border-b border-gray-200 dark:border-dark-border">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{note.title}</h1>
          {note.summary && (
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">
              {note.summary}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {note.read_time} min read
            </span>
            <span className="px-2 py-0.5 rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs font-medium">
              {note.level}
            </span>
            {note.tags.length > 0 && (
              <span className="flex items-center gap-2 flex-wrap">
                <Tag className="w-4 h-4" />
                {note.tags.map((tag) => (
                  <span key={tag} className="text-xs">
                    #{tag}
                  </span>
                ))}
              </span>
            )}
          </div>
        </header>

        <NoteRenderer content={note.content} />
      </article>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleLd) }}
      />
    </main>
  )
}
