/**
 * Regression: a production build without NEXT_PUBLIC_API_URL used to silently
 * proxy /api/* to localhost:8000, so the contact form failed for every visitor.
 */

describe('next.config.js', () => {
  const original = { ...process.env }

  function load() {
    jest.resetModules()
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require('../../next.config.js')
  }

  afterEach(() => {
    process.env = { ...original }
  })

  it('throws in production when NEXT_PUBLIC_API_URL is missing', () => {
    ;(process.env as Record<string, string>).NODE_ENV = 'production'
    delete process.env.NEXT_PUBLIC_API_URL
    expect(load).toThrow(/NEXT_PUBLIC_API_URL/)
  })

  it('builds in production when NEXT_PUBLIC_API_URL is set', () => {
    ;(process.env as Record<string, string>).NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'
    expect(load).not.toThrow()
  })

  it('rewrites /api/* to the configured backend', async () => {
    ;(process.env as Record<string, string>).NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'
    const rewrites = await load().rewrites()
    expect(rewrites).toContainEqual({
      source: '/api/:path*',
      destination: 'https://api.example.com/api/:path*',
    })
  })

  it('still allows local development without the variable', () => {
    ;(process.env as Record<string, string>).NODE_ENV = 'development'
    delete process.env.NEXT_PUBLIC_API_URL
    expect(load).not.toThrow()
  })

  it.each([
    ['https://api.example.com/', 'https://api.example.com/api/:path*'],
    ['https://api.example.com///', 'https://api.example.com/api/:path*'],
    ['  https://api.example.com  ', 'https://api.example.com/api/:path*'],
  ])('tolerates a sloppy NEXT_PUBLIC_API_URL %j', async (value, expected) => {
    ;(process.env as Record<string, string>).NODE_ENV = 'production'
    process.env.NEXT_PUBLIC_API_URL = value
    const rewrites = await load().rewrites()
    expect(rewrites[0].destination).toBe(expected)
  })
})
