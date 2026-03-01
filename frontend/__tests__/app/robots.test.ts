/**
 * Tests for app/robots.ts
 *
 * Verifies that robots() returns the correct rules and sitemap URL.
 */

describe('robots()', () => {
  const DEFAULT_URL = 'https://carrier-profile.vercel.app'

  function loadRobots() {
    jest.resetModules()
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require('../../app/robots').default
  }

  afterEach(() => {
    delete process.env.NEXT_PUBLIC_BASE_URL
    jest.resetModules()
  })

  it('returns an object with rules and sitemap', () => {
    const robots = loadRobots()
    const result = robots()
    expect(result).toHaveProperty('rules')
    expect(result).toHaveProperty('sitemap')
  })

  it('allows all user agents', () => {
    const robots = loadRobots()
    const { rules } = robots()
    expect(rules.userAgent).toBe('*')
  })

  it('allows the root path', () => {
    const robots = loadRobots()
    const { rules } = robots()
    expect(rules.allow).toBe('/')
  })

  it('disallows /api/ path', () => {
    const robots = loadRobots()
    const { rules } = robots()
    const disallow = Array.isArray(rules.disallow) ? rules.disallow : [rules.disallow]
    expect(disallow.some((d: string) => d.includes('/api/'))).toBe(true)
  })

  it('sitemap URL points to sitemap.xml', () => {
    const robots = loadRobots()
    const { sitemap } = robots()
    expect(sitemap).toContain('sitemap.xml')
  })

  it('sitemap URL uses the base URL', () => {
    const robots = loadRobots()
    const { sitemap } = robots()
    expect(sitemap).toContain(DEFAULT_URL)
  })

  it('uses NEXT_PUBLIC_BASE_URL env var for sitemap when set', () => {
    process.env.NEXT_PUBLIC_BASE_URL = 'https://custom.example.com'
    const robots = loadRobots()
    const { sitemap } = robots()
    expect(sitemap).toContain('https://custom.example.com')
  })
})
