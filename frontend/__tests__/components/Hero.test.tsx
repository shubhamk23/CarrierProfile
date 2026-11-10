/**
 * Regression: the Download Resume button used NEXT_PUBLIC_RESUME_URL, which
 * in production pointed at a Supabase project that no longer resolved (DNS
 * error), so the download failed. The link must be a same-origin file.
 */
import React from 'react'
import fs from 'fs'
import path from 'path'
import { render, screen } from '@testing-library/react'

jest.mock('framer-motion', () => ({
  motion: new Proxy(
    {},
    {
      get: (_t, tag: string) =>
        function MotionStub({ children, initial, animate, transition, ...props }: any) {
          return React.createElement(tag, props, children)
        },
    },
  ),
}))

jest.mock('lucide-react', () => ({
  MapPin: () => null,
  Mail: () => null,
  Linkedin: () => null,
  Github: () => null,
  Download: () => null,
  ChevronDown: () => null,
}))

import Hero from '../../components/Hero'

describe('Hero resume download', () => {
  const original = process.env.NEXT_PUBLIC_RESUME_URL

  afterEach(() => {
    if (original === undefined) delete process.env.NEXT_PUBLIC_RESUME_URL
    else process.env.NEXT_PUBLIC_RESUME_URL = original
  })

  it('links to the same-origin /resume.pdf', () => {
    render(<Hero />)
    const link = screen.getByRole('link', { name: /download resume/i })
    expect(link).toHaveAttribute('href', '/resume.pdf')
    expect(link).toHaveAttribute('download')
  })

  it('ignores a stale NEXT_PUBLIC_RESUME_URL from the environment', () => {
    process.env.NEXT_PUBLIC_RESUME_URL = 'https://dead.supabase.co/resume.pdf'
    render(<Hero />)
    expect(screen.getByRole('link', { name: /download resume/i })).toHaveAttribute(
      'href',
      '/resume.pdf',
    )
  })

  it('has a real PDF at the linked path', () => {
    const file = path.join(__dirname, '../../public/resume.pdf')
    const head = fs.readFileSync(file).subarray(0, 5).toString()
    expect(head).toBe('%PDF-')
    expect(fs.statSync(file).size).toBeGreaterThan(10_000)
  })
})
