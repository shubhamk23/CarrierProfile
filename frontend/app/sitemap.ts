import type { MetadataRoute } from 'next'

import { getSection, listSections } from '@/lib/knowledge'

const BASE_URL =
  process.env.NEXT_PUBLIC_BASE_URL || 'https://carrier-profile.vercel.app'

async function knowledgeUrls(): Promise<MetadataRoute.Sitemap> {
  try {
    const sections = await listSections()
    const sectionEntries: MetadataRoute.Sitemap = sections.map((s) => ({
      url: `${BASE_URL}/knowledge/${s.slug}`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.7,
    }))

    const notes = await Promise.all(
      sections.map((s) =>
        getSection(s.slug)
          .then((r) =>
            r.notes.map((n) => ({
              url: `${BASE_URL}/knowledge/${n.section_slug}/${n.slug}`,
              lastModified: new Date(n.updated_at ?? n.created_at),
              changeFrequency: 'monthly' as const,
              priority: 0.6,
            })),
          )
          .catch(() => [] as MetadataRoute.Sitemap),
      ),
    )

    return [
      {
        url: `${BASE_URL}/knowledge`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.9,
      },
      ...sectionEntries,
      ...notes.flat(),
    ]
  } catch {
    return []
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const knowledge = await knowledgeUrls()

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 1,
    },
    {
      url: `${BASE_URL}/#about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/#experience`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/#skills`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/#projects`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/#blog`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/#contact`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.7,
    },
    ...knowledge,
  ]
}
