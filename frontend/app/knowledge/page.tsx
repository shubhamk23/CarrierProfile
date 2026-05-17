import type { Metadata } from 'next'

import SearchBar from '@/components/knowledge/SearchBar'
import SectionCard from '@/components/knowledge/SectionCard'
import { listSections } from '@/lib/knowledge'

export const metadata: Metadata = {
  title: 'AI / ML Knowledge Hub | Shubham Khanapure',
  description:
    'A curated knowledge base of 30+ AI/ML notes across NLP, computer vision, recommendation systems, MLOps, and more — with full-text search.',
}

export const revalidate = 60

export default async function KnowledgeIndexPage() {
  let sections = await listSections().catch(() => [])

  return (
    <main className="section-container pt-24">
      <header className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          AI / ML <span className="gradient-text">Knowledge Hub</span>
        </h1>
        <p className="max-w-2xl mx-auto text-gray-600 dark:text-gray-300 mb-8">
          A living knowledge base of {sections.reduce((n, s) => n + s.note_count, 0)}+
          notes across {sections.length} sections — covering transformers, RAG,
          computer vision, MLOps, and the latest in agentic systems.
        </p>
        <SearchBar />
      </header>

      {sections.length === 0 ? (
        <div className="text-center text-gray-500 dark:text-gray-400 py-12">
          The knowledge hub is warming up. Try again in a minute.
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {sections.map((section, i) => (
            <SectionCard key={section.id} section={section} index={i} />
          ))}
        </div>
      )}
    </main>
  )
}
