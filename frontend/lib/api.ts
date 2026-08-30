export interface ContactMessage {
  name: string
  email: string
  subject: string
  message: string
}

export interface ContactResponse {
  success: boolean
  message: string
}

export async function submitContactForm(data: ContactMessage): Promise<ContactResponse> {
  const response = await fetch('/api/contact', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const detail = body?.detail ?? body?.message
    throw new Error(
      typeof detail === 'string' ? detail : `Failed to submit contact form (${response.status})`
    )
  }

  return body as ContactResponse
}
