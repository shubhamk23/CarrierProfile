import Link from 'next/link'

export default function BlogPostNotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Post Not Found</h1>
        <Link href="/#blog" className="text-primary-600 hover:underline">
          Back to Blog
        </Link>
      </div>
    </div>
  )
}
