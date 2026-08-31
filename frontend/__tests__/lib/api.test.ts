/**
 * Tests for lib/api.ts
 *
 * All network calls are intercepted via global fetch mocking so these tests
 * run entirely in-process without any real HTTP traffic.
 */

import { submitContactForm } from '../../lib/api'

function mockFetch(ok: boolean, body: unknown, status = 200): void {
  global.fetch = jest.fn().mockResolvedValueOnce({
    ok,
    status,
    json: jest.fn().mockResolvedValueOnce(body),
  } as unknown as Response)
}

afterEach(() => {
  jest.restoreAllMocks()
})

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

  it('calls fetch with POST method against the relative /api/contact path', async () => {
    mockFetch(true, { success: true, message: 'ok' })
    await submitContactForm(payload)
    expect(fetch).toHaveBeenCalledWith(
      '/api/contact',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('sends JSON content-type header and the payload body', async () => {
    mockFetch(true, { success: true, message: 'ok' })
    await submitContactForm(payload)
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload),
      })
    )
  })

  it('throws the backend detail message when response is not ok', async () => {
    mockFetch(false, { detail: 'Rate limit exceeded' }, 429)
    await expect(submitContactForm(payload)).rejects.toThrow('Rate limit exceeded')
  })

  it('falls back to a status-coded message when the body has no detail', async () => {
    mockFetch(false, {}, 500)
    await expect(submitContactForm(payload)).rejects.toThrow('Failed to submit contact form (500)')
  })

  it('falls back to a status-coded message when the body is not valid JSON', async () => {
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: false,
      status: 502,
      json: jest.fn().mockRejectedValueOnce(new Error('not json')),
    } as unknown as Response)
    await expect(submitContactForm(payload)).rejects.toThrow('Failed to submit contact form (502)')
  })
})
