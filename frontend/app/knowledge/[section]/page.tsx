import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { ChevronLeft } from 'lucide-react'

import NoteCard from '@/components/knowledge/NoteCard'
import { getSection, KnowledgeApiError, listSections } from '@/lib/knowledge'

interface PageProps {
  params: { section: string }
}

export const revalidate = 60

export async function generateStaticParams() {
  try {
    const sections = await listSections()
    return sections.map((s) => ({ section: s.slug }))
  } catch {
    return []
  }
}

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  try {
    const { section } = await getSection(params.section)
    return {
      title: `${section.title} — Knowledge Hub`,
      description:
        section.description ??
        `${section.note_count} curated notes on ${section.title}.`,
    }
  } catch {
    return { title: 'Section not found — Knowledge Hub' }
  }
}

export default async function SectionPage({ params }: PageProps) {
  let payload
  try {
    payload = await getSection(params.section)
  } catch (err) {
    if (err instanceof KnowledgeApiError && err.status === 404) {
      notFound()
    }
    throw err
  }
  const { section, notes } = payload

  return (
    <main className="section-container pt-24">
      <Link
        href="/knowledge"
        className="inline-flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline mb-6"
      >
        <ChevronLeft className="w-4 h-4" /> All sections
      </Link>

      <header className="mb-10">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-4xl">{section.icon ?? '📚'}</span>
          <h1 className="text-3xl md:text-4xl font-bold">{section.title}</h1>
        </div>
        {section.description && (
          <p className="text-gray-600 dark:text-gray-300 max-w-3xl">
            {section.description}
          </p>
        )}
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
          {notes.length} {notes.length === 1 ? 'note' : 'notes'}
        </p>
      </header>

      {notes.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-12">
          No public notes yet in this section.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {notes.map((note, i) => (
            <NoteCard key={note.id} note={note} index={i} />
          ))}
        </div>
      )}
    </main>
  )
}
