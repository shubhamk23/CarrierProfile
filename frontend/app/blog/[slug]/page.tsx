import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { getAllBlogPosts, getBlogPost } from '@/lib/blog-posts'
import PostContent from './PostContent'

interface BlogPostPageProps {
  params: { slug: string }
}

export function generateStaticParams() {
  return getAllBlogPosts().map((post) => ({ slug: post.slug }))
}

export function generateMetadata({ params }: BlogPostPageProps): Metadata {
  const post = getBlogPost(params.slug)

  if (!post) {
    return { title: 'Post Not Found' }
  }

  return {
    title: `${post.title} | Shubham Khanapure`,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: 'article',
      publishedTime: post.date,
    },
  }
}

export default function BlogPostPage({ params }: BlogPostPageProps) {
  const post = getBlogPost(params.slug)

  if (!post) {
    notFound()
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <PostContent post={post} />
    </div>
  )
}
