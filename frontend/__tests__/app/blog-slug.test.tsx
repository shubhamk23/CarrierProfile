/**
 * Tests for app/blog/[slug]/page.tsx (BlogPostPage)
 *
 * Behaviours tested:
 * - Valid slug renders the post title, category, read time, and formatted date
 * - Invalid slug renders the "Post Not Found" message
 * - Markdown headings (#, ##, ###) are converted to h1/h2/h3 elements
 * - Bullet list items (- …) are converted to <li> elements
 * - Numbered list items (1. …) are converted to <li> elements
 */

import React from 'react'
import { render, screen } from '@testing-library/react'

// ------------------------------------------------------------------
// Module mocks
// ------------------------------------------------------------------

// next/navigation — let each test control the returned slug
let mockSlug = 'building-production-rag-systems'
jest.mock('next/navigation', () => ({
  useParams: () => ({ slug: mockSlug }),
}))

// next/link — render as a plain <a>
jest.mock('next/link', () => {
  const Link = ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  )
  Link.displayName = 'Link'
  return Link
})

// framer-motion — pass-through div
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLProps<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}))

// lucide-react icons
jest.mock('lucide-react', () => ({
  ArrowLeft: () => null,
  Calendar: () => null,
  Clock: () => null,
  Tag: () => null,
}))

import BlogPostPage from '../../app/blog/[slug]/page'

// ------------------------------------------------------------------
// Tests
// ------------------------------------------------------------------

describe('BlogPostPage — valid slug', () => {
  beforeEach(() => {
    mockSlug = 'building-production-rag-systems'
  })

  it('renders the post title', () => {
    render(<BlogPostPage />)
    expect(
      screen.getByText(/Building Production-Grade RAG Systems/i),
    ).toBeInTheDocument()
  })

  it('renders the category badge', () => {
    render(<BlogPostPage />)
    expect(screen.getByText('Generative AI')).toBeInTheDocument()
  })

  it('renders the read time', () => {
    render(<BlogPostPage />)
    expect(screen.getByText('12 min read')).toBeInTheDocument()
  })

  it('renders a formatted date string', () => {
    render(<BlogPostPage />)
    // Date 2024-12-15 formats to "December 15, 2024" in en-US locale
    expect(screen.getByText(/December 15, 2024/i)).toBeInTheDocument()
  })
})

describe('BlogPostPage — invalid slug', () => {
  beforeEach(() => {
    mockSlug = 'this-does-not-exist'
  })

  it('renders "Post Not Found"', () => {
    render(<BlogPostPage />)
    expect(screen.getByText(/Post Not Found/i)).toBeInTheDocument()
  })

  it('renders a "Back to Blog" link', () => {
    render(<BlogPostPage />)
    expect(screen.getByRole('link', { name: /back to blog/i })).toBeInTheDocument()
  })
})

describe('BlogPostPage — markdown rendering', () => {
  // Use the YOLO post which has ###-level headings and bullet lists
  beforeEach(() => {
    mockSlug = 'yolo-object-detection-evolution'
  })

  it('renders # heading as h1', () => {
    render(<BlogPostPage />)
    const h1s = screen.getAllByRole('heading', { level: 1 })
    const match = h1s.find((el) => el.textContent?.includes('YOLO Object Detection'))
    expect(match).toBeTruthy()
  })

  it('renders ## heading as h2', () => {
    render(<BlogPostPage />)
    const h2s = screen.getAllByRole('heading', { level: 2 })
    const match = h2s.find((el) => el.textContent?.includes('Evolution of YOLO'))
    expect(match).toBeTruthy()
  })

  it('renders ### heading as h3', () => {
    render(<BlogPostPage />)
    const h3s = screen.getAllByRole('heading', { level: 3 })
    const match = h3s.find((el) => el.textContent?.includes('YOLOv5'))
    expect(match).toBeTruthy()
  })

  it('renders - bullet items as <li> elements', () => {
    render(<BlogPostPage />)
    const listItems = screen.getAllByRole('listitem')
    const match = listItems.find((el) =>
      el.textContent?.includes('PyTorch-based implementation'),
    )
    expect(match).toBeTruthy()
  })

  it('renders numbered list items as <li> elements', () => {
    render(<BlogPostPage />)
    const listItems = screen.getAllByRole('listitem')
    const match = listItems.find((el) => el.textContent?.includes('Data Quality'))
    expect(match).toBeTruthy()
  })
})
