/**
 * Tests for app/sitemap.ts
 *
 * Verifies that the sitemap() function returns the correct structure
 * and respects the NEXT_PUBLIC_BASE_URL environment variable.
 */

describe('sitemap()', () => {
  const DEFAULT_URL = 'https://carrier-profile.vercel.app'

  function loadSitemap() {
    // Re-import fresh so env var changes take effect
    jest.resetModules()
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require('../../app/sitemap').default
  }

  afterEach(() => {
    delete process.env.NEXT_PUBLIC_BASE_URL
    jest.resetModules()
  })

  it('returns the 7 section entries plus one per blog post', () => {
    const sitemap = loadSitemap()
    expect(sitemap()).toHaveLength(10)
  })

  it('includes an entry for every blog post slug', () => {
    const sitemap = loadSitemap()
    const entries = sitemap()
    for (const slug of [
      'building-production-rag-systems',
      'yolo-object-detection-evolution',
      'mlops-azure-ml-studio',
    ]) {
      expect(entries.some((e: { url: string }) => e.url.endsWith(`/blog/${slug}`))).toBe(true)
    }
  })

  it('root entry has priority 1', () => {
    const sitemap = loadSitemap()
    const entries = sitemap()
    expect(entries[0].priority).toBe(1)
  })

  it('root entry URL equals the base URL', () => {
    const sitemap = loadSitemap()
    const entries = sitemap()
    expect(entries[0].url).toBe(DEFAULT_URL)
  })

  it('all entries have a url property', () => {
    const sitemap = loadSitemap()
    for (const entry of sitemap()) {
      expect(entry).toHaveProperty('url')
    }
  })

  it('all entries have a lastModified date', () => {
    const sitemap = loadSitemap()
    for (const entry of sitemap()) {
      expect(entry.lastModified).toBeInstanceOf(Date)
    }
  })

  it('uses NEXT_PUBLIC_BASE_URL env var when set', () => {
    process.env.NEXT_PUBLIC_BASE_URL = 'https://custom.example.com'
    const sitemap = loadSitemap()
    const entries = sitemap()
    expect(entries[0].url).toBe('https://custom.example.com')
  })

  it('falls back to default vercel URL when env var is not set', () => {
    delete process.env.NEXT_PUBLIC_BASE_URL
    const sitemap = loadSitemap()
    const entries = sitemap()
    expect(entries[0].url).toBe(DEFAULT_URL)
  })

  it('blog entry has higher priority than contact entry', () => {
    const sitemap = loadSitemap()
    const entries = sitemap()
    const blog = entries.find((e: { url: string }) => e.url.includes('#blog'))
    const contact = entries.find((e: { url: string }) => e.url.includes('#contact'))
    expect(blog?.priority).toBeGreaterThan(contact?.priority)
  })
})
