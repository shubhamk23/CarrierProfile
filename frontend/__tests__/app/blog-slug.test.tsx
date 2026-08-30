/**
 * Tests for app/blog/[slug]/page.tsx (BlogPostPage), its generateMetadata /
 * generateStaticParams exports, and the not-found.tsx fallback.
 */

import React from 'react'
import { render, screen } from '@testing-library/react'

const mockNotFound = jest.fn(() => {
  throw new Error('NEXT_NOT_FOUND')
})
jest.mock('next/navigation', () => ({
  notFound: () => mockNotFound(),
}))

jest.mock('next/link', () => {
  const Link = ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  )
  Link.displayName = 'Link'
  return Link
})

jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLProps<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
  },
}))

jest.mock('lucide-react', () => ({
  ArrowLeft: () => null,
  Calendar: () => null,
  Clock: () => null,
  Tag: () => null,
}))

import BlogPostPage, { generateMetadata, generateStaticParams } from '../../app/blog/[slug]/page'
import BlogPostNotFound from '../../app/blog/[slug]/not-found'

class TestErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { error: Error | null }
> {
  state: { error: Error | null } = { error: null }

  static getDerivedStateFromError(error: Error) {
    return { error }
  }

  render() {
    if (this.state.error) return null
    return this.props.children
  }
}

describe('BlogPostPage — valid slug', () => {
  const params = { slug: 'building-production-rag-systems' }

  beforeEach(() => {
    mockNotFound.mockClear()
  })

  it('renders the post title', () => {
    render(<BlogPostPage params={params} />)
    // The title appears both in the header and as the markdown content's
    // leading "# " line, so multiple matches are expected.
    expect(screen.getAllByText(/Building Production-Grade RAG Systems/i).length).toBeGreaterThan(0)
  })

  it('renders the category badge', () => {
    render(<BlogPostPage params={params} />)
    expect(screen.getByText('Generative AI')).toBeInTheDocument()
  })

  it('renders the read time', () => {
    render(<BlogPostPage params={params} />)
    expect(screen.getByText('12 min read')).toBeInTheDocument()
  })

  it('renders a formatted date string', () => {
    render(<BlogPostPage params={params} />)
    expect(screen.getByText(/December 15, 2024/i)).toBeInTheDocument()
  })

  it('does not call notFound', () => {
    render(<BlogPostPage params={params} />)
    expect(mockNotFound).not.toHaveBeenCalled()
  })
})

describe('BlogPostPage — invalid slug', () => {
  beforeEach(() => {
    mockNotFound.mockClear()
  })

  it('calls notFound() instead of rendering', () => {
    render(
      <TestErrorBoundary>
        <BlogPostPage params={{ slug: 'this-does-not-exist' }} />
      </TestErrorBoundary>
    )
    expect(mockNotFound).toHaveBeenCalled()
  })
})

describe('BlogPostNotFound', () => {
  it('renders "Post Not Found"', () => {
    render(<BlogPostNotFound />)
    expect(screen.getByText(/Post Not Found/i)).toBeInTheDocument()
  })

  it('renders a "Back to Blog" link', () => {
    render(<BlogPostNotFound />)
    expect(screen.getByRole('link', { name: /back to blog/i })).toBeInTheDocument()
  })
})

describe('BlogPostPage — markdown rendering', () => {
  const params = { slug: 'yolo-object-detection-evolution' }

  it('renders # heading as h1', () => {
    render(<BlogPostPage params={params} />)
    const h1s = screen.getAllByRole('heading', { level: 1 })
    expect(h1s.some((el) => el.textContent?.includes('YOLO Object Detection'))).toBe(true)
  })

  it('renders ## heading as h2', () => {
    render(<BlogPostPage params={params} />)
    const h2s = screen.getAllByRole('heading', { level: 2 })
    expect(h2s.some((el) => el.textContent?.includes('Evolution of YOLO'))).toBe(true)
  })

  it('renders ### heading as h3', () => {
    render(<BlogPostPage params={params} />)
    const h3s = screen.getAllByRole('heading', { level: 3 })
    expect(h3s.some((el) => el.textContent?.includes('YOLOv5'))).toBe(true)
  })

  it('renders - bullet items inside a <ul>', () => {
    render(<BlogPostPage params={params} />)
    const lists = screen.getAllByRole('list')
    const ul = lists.find((el) => el.tagName === 'UL' && el.textContent?.includes('PyTorch-based implementation'))
    expect(ul).toBeTruthy()
    expect(ul?.querySelector('li')).toBeTruthy()
  })

  it('renders numbered list items inside an <ol>', () => {
    render(<BlogPostPage params={params} />)
    const lists = screen.getAllByRole('list')
    const ol = lists.find((el) => el.tagName === 'OL' && el.textContent?.includes('Data Quality'))
    expect(ol).toBeTruthy()
    expect(ol?.querySelector('li')).toBeTruthy()
  })
})

describe('generateStaticParams', () => {
  it('returns a params object for every blog post', () => {
    const params = generateStaticParams()
    expect(params).toEqual(
      expect.arrayContaining([
        { slug: 'building-production-rag-systems' },
        { slug: 'yolo-object-detection-evolution' },
        { slug: 'mlops-azure-ml-studio' },
      ])
    )
  })
})

describe('generateMetadata', () => {
  it('returns the post title and excerpt for a known slug', () => {
    const metadata = generateMetadata({ params: { slug: 'building-production-rag-systems' } })
    expect(metadata.title).toContain('Building Production-Grade RAG Systems')
    expect(metadata.description).toMatch(/comprehensive guide/i)
  })

  it('returns a fallback title for an unknown slug', () => {
    const metadata = generateMetadata({ params: { slug: 'nonexistent' } })
    expect(metadata.title).toBe('Post Not Found')
  })
})
