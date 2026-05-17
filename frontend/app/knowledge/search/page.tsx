import type { Metadata } from 'next'
import Link from 'next/link'
import { ChevronLeft } from 'lucide-react'

import SearchBar from '@/components/knowledge/SearchBar'
import { searchKnowledge } from '@/lib/knowledge'

export const metadata: Metadata = {
  title: 'Search — Knowledge Hub',
  description: 'Full-text search across the AI/ML knowledge base.',
}

interface PageProps {
  searchParams: { q?: string }
}

export const dynamic = 'force-dynamic'

export default async function SearchPage({ searchParams }: PageProps) {
  const query = (searchParams.q ?? '').trim()
  const data =
    query.length > 0
      ? await searchKnowledge(query, { limit: 20 }).catch(() => ({
          results: [],
          total: 0,
          query,
        }))
      : { results: [], total: 0, query }

  return (
    <main className="section-container pt-24">
      <Link
        href="/knowledge"
        className="inline-flex items-center gap-1 text-sm text-primary-600 dark:text-primary-400 hover:underline mb-6"
      >
        <ChevronLeft className="w-4 h-4" /> Knowledge hub
      </Link>

      <header className="text-center mb-10">
        <h1 className="text-3xl md:text-4xl font-bold mb-6">
          Search the knowledge hub
        </h1>
        <SearchBar initialQuery={query} autoFocus={!query} />
      </header>

      {query.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">
          Type a query above to search across the corpus.
        </p>
      ) : data.results.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">
          No matches for <strong className="font-semibold">“{query}”</strong>.
        </p>
      ) : (
        <>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            {data.total} {data.total === 1 ? 'result' : 'results'} for
            {' '}
            <strong className="font-semibold">“{query}”</strong>
          </p>
          <ul className="space-y-4">
            {data.results.map((r) => (
              <li key={r.id} className="card hover:border-primary-300">
                <Link
                  href={`/knowledge/${r.section_slug}/${r.slug}`}
                  className="block"
                >
                  <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                    {r.section_slug}
                  </div>
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white hover:text-primary-600 dark:hover:text-primary-400">
                    {r.title}
                  </h2>
                  <p
                    className="text-sm text-gray-600 dark:text-gray-300 mt-2"
                    // ts_headline returns sanitized text with <mark>...</mark>
                    dangerouslySetInnerHTML={{ __html: r.excerpt }}
                  />
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
