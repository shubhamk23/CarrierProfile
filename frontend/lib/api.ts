const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

export interface ContactMessage {
  name: string
  email: string
  subject: string
  message: string
}

export interface BlogPost {
  slug: string
  title: string
  excerpt: string
  content: string
  date: string
  readTime: string
  category: string
}

export async function submitContactForm(data: ContactMessage): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/contact`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('Failed to submit contact form')
  }

  return response.json()
}

export async function getBlogPosts(): Promise<BlogPost[]> {
  const response = await fetch(`${API_BASE_URL}/api/blog`)

  if (!response.ok) {
    throw new Error('Failed to fetch blog posts')
  }

  return response.json()
}

export async function getBlogPost(slug: string): Promise<BlogPost> {
  const response = await fetch(`${API_BASE_URL}/api/blog/${slug}`)

  if (!response.ok) {
    throw new Error('Failed to fetch blog post')
  }

  return response.json()
}

export async function getProfile() {
  const response = await fetch(`${API_BASE_URL}/api/profile`)

  if (!response.ok) {
    throw new Error('Failed to fetch profile')
  }

  return response.json()
}
