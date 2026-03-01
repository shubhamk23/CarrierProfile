/**
 * Tests for lib/api.ts
 *
 * All network calls are intercepted via global fetch mocking so these tests
 * run entirely in-process without any real HTTP traffic.
 */

import {
  submitContactForm,
  getBlogPosts,
  getBlogPost,
  getProfile,
} from '../../lib/api'

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mockFetch(ok: boolean, body: unknown): void {
  global.fetch = jest.fn().mockResolvedValueOnce({
    ok,
    json: jest.fn().mockResolvedValueOnce(body),
  } as unknown as Response)
}

function mockFetchError(message: string): void {
  global.fetch = jest.fn().mockRejectedValueOnce(new Error(message))
}

afterEach(() => {
  jest.restoreAllMocks()
})

// ---------------------------------------------------------------------------
// submitContactForm
// ---------------------------------------------------------------------------

describe('submitContactForm', () => {
  const payload = {
    name: 'Alice',
    email: 'alice@example.com',
    subject: 'Hello',
    message: 'Test message',
  }

  it('returns success response on 2xx', async () => {
    const responseBody = { success: true, message: 'Sent!' }
    mockFetch(true, responseBody)
    const result = await submitContactForm(payload)
    expect(result).toEqual(responseBody)
  })

  it('calls fetch with POST method', async () => {
    mockFetch(true, { success: true, message: 'ok' })
    await submitContactForm(payload)
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/contact'),
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('sends JSON content-type header', async () => {
    mockFetch(true, { success: true, message: 'ok' })
    await submitContactForm(payload)
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
      }),
    )
  })

  it('throws Error when response is not ok', async () => {
    mockFetch(false, { detail: 'Bad request' })
    await expect(submitContactForm(payload)).rejects.toThrow('Failed to submit contact form')
  })
})

// ---------------------------------------------------------------------------
// getBlogPosts
// ---------------------------------------------------------------------------

describe('getBlogPosts', () => {
  const mockPosts = [
    { slug: 'post-1', title: 'Post 1', excerpt: 'Ex', date: '2024-01-01', readTime: '5 min', category: 'Tech' },
  ]

  it('returns array of blog posts on success', async () => {
    mockFetch(true, mockPosts)
    const result = await getBlogPosts()
    expect(result).toEqual(mockPosts)
  })

  it('calls /api/blog endpoint', async () => {
    mockFetch(true, [])
    await getBlogPosts()
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/blog'))
  })

  it('throws when response is not ok', async () => {
    mockFetch(false, { detail: 'Server error' })
    await expect(getBlogPosts()).rejects.toThrow('Failed to fetch blog posts')
  })
})

// ---------------------------------------------------------------------------
// getBlogPost
// ---------------------------------------------------------------------------

describe('getBlogPost', () => {
  const mockPost = {
    slug: 'my-post',
    title: 'My Post',
    excerpt: 'Excerpt',
    content: 'Full content',
    date: '2024-01-01',
    readTime: '5 min',
    category: 'Tech',
  }

  it('returns full blog post for valid slug', async () => {
    mockFetch(true, mockPost)
    const result = await getBlogPost('my-post')
    expect(result).toEqual(mockPost)
  })

  it('calls /api/blog/:slug endpoint', async () => {
    mockFetch(true, mockPost)
    await getBlogPost('my-post')
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/blog/my-post'))
  })

  it('throws when slug not found (non-ok response)', async () => {
    mockFetch(false, { detail: 'Not found' })
    await expect(getBlogPost('nonexistent')).rejects.toThrow('Failed to fetch blog post')
  })
})

// ---------------------------------------------------------------------------
// getProfile
// ---------------------------------------------------------------------------

describe('getProfile', () => {
  const mockProfile = { name: 'Test User', title: 'Engineer' }

  it('returns profile data on success', async () => {
    mockFetch(true, mockProfile)
    const result = await getProfile()
    expect(result).toEqual(mockProfile)
  })

  it('calls /api/profile endpoint', async () => {
    mockFetch(true, mockProfile)
    await getProfile()
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/profile'))
  })

  it('throws when response is not ok', async () => {
    mockFetch(false, { detail: 'Error' })
    await expect(getProfile()).rejects.toThrow('Failed to fetch profile')
  })
})

// ---------------------------------------------------------------------------
// Base URL
// ---------------------------------------------------------------------------

describe('API base URL', () => {
  it('uses NEXT_PUBLIC_API_URL env var when set', async () => {
    const originalEnv = process.env.NEXT_PUBLIC_API_URL
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'

    // Re-import the module to pick up the env var
    jest.resetModules()
    const { getProfile: getProfileFresh } = await import('../../lib/api')

    mockFetch(true, {})
    await getProfileFresh()

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('https://api.example.com'),
    )

    process.env.NEXT_PUBLIC_API_URL = originalEnv
  })
})
