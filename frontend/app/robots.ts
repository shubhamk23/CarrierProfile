import type { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  const baseUrl =
    process.env.NEXT_PUBLIC_BASE_URL || 'https://carrier-profile.vercel.app'

  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/api/', '/knowledge/admin/'],
    },
    sitemap: `${baseUrl}/sitemap.xml`,
  }
}
