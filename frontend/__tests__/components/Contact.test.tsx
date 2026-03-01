/**
 * Tests for components/Contact.tsx
 *
 * Behaviours tested:
 * - All four form fields render
 * - Zod validation errors surface on submit with invalid data
 * - Successful fetch shows the success state and resets the form
 * - Failed fetch shows the error state
 */

import React from 'react'
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

// framer-motion causes issues in JSDOM; replace with simple pass-through
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: React.HTMLProps<HTMLDivElement>) => (
      <div {...props}>{children}</div>
    ),
    section: ({ children, ...props }: React.HTMLProps<HTMLElement>) => (
      <section {...props}>{children}</section>
    ),
  },
  useInView: () => true,
}))

// Stub lucide-react icons
jest.mock('lucide-react', () => ({
  Mail: () => null,
  Send: () => <span data-testid="send-icon" />,
  Loader2: () => <span data-testid="loader-icon" />,
  CheckCircle: () => <span data-testid="check-icon" />,
  AlertCircle: () => <span data-testid="alert-icon" />,
  MapPin: () => null,
  Phone: () => null,
  Linkedin: () => null,
  Github: () => null,
}))

import Contact from '../../components/Contact'

// Helper to fill the form with valid data
async function fillForm(overrides: Partial<Record<string, string>> = {}) {
  const values = {
    name: 'Alice Smith',
    email: 'alice@example.com',
    subject: 'Hello there',
    message: 'This is a test message that is long enough.',
    ...overrides,
  }

  const nameInput = screen.getByLabelText(/name/i)
  const emailInput = screen.getByLabelText(/email/i)
  const subjectInput = screen.getByLabelText(/subject/i)
  const messageInput = screen.getByLabelText(/message/i)

  await userEvent.clear(nameInput)
  await userEvent.clear(emailInput)
  await userEvent.clear(subjectInput)
  await userEvent.clear(messageInput)

  await userEvent.type(nameInput, values.name)
  await userEvent.type(emailInput, values.email)
  await userEvent.type(subjectInput, values.subject)
  await userEvent.type(messageInput, values.message)
}

describe('Contact — form renders', () => {
  it('renders Name input', () => {
    render(<Contact />)
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
  })

  it('renders Email input', () => {
    render(<Contact />)
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  })

  it('renders Subject input', () => {
    render(<Contact />)
    expect(screen.getByLabelText(/subject/i)).toBeInTheDocument()
  })

  it('renders Message textarea', () => {
    render(<Contact />)
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument()
  })

  it('renders the Send Message button', () => {
    render(<Contact />)
    expect(screen.getByRole('button', { name: /send message/i })).toBeInTheDocument()
  })
})

describe('Contact — validation errors', () => {
  it('shows error when name is too short (< 2 chars)', async () => {
    render(<Contact />)
    await fillForm({ name: 'A' })
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))
    await waitFor(() => {
      expect(screen.getByText(/at least 2 characters/i)).toBeInTheDocument()
    })
  })

  it('shows error for invalid email', async () => {
    render(<Contact />)
    await fillForm({ email: 'not-an-email' })
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))
    await waitFor(() => {
      expect(screen.getByText(/valid email/i)).toBeInTheDocument()
    })
  })

  it('shows error when subject is too short (< 5 chars)', async () => {
    render(<Contact />)
    await fillForm({ subject: 'Hi' })
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))
    await waitFor(() => {
      expect(screen.getByText(/at least 5 characters/i)).toBeInTheDocument()
    })
  })

  it('shows error when message is too short (< 10 chars)', async () => {
    render(<Contact />)
    await fillForm({ message: 'Short' })
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))
    await waitFor(() => {
      expect(screen.getByText(/at least 10 characters/i)).toBeInTheDocument()
    })
  })
})

describe('Contact — submission states', () => {
  beforeEach(() => {
    global.fetch = jest.fn()
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  it('shows success message after successful submission', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Sent!' }),
    })

    render(<Contact />)
    await fillForm()
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))

    await waitFor(() => {
      expect(screen.getByText(/message sent successfully/i)).toBeInTheDocument()
    })
  })

  it('shows error message after failed submission (non-ok response)', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Server error' }),
    })

    render(<Contact />)
    await fillForm()
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))

    await waitFor(() => {
      expect(screen.getByText(/failed to send/i)).toBeInTheDocument()
    })
  })

  it('shows error message when fetch throws', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

    render(<Contact />)
    await fillForm()
    fireEvent.click(screen.getByRole('button', { name: /send message/i }))

    await waitFor(() => {
      expect(screen.getByText(/failed to send/i)).toBeInTheDocument()
    })
  })

  it('resets form fields after successful submission', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true, message: 'Sent!' }),
    })

    render(<Contact />)
    await fillForm()

    const nameInput = screen.getByLabelText(/name/i) as HTMLInputElement
    expect(nameInput.value).toBe('Alice Smith')

    fireEvent.click(screen.getByRole('button', { name: /send message/i }))

    await waitFor(() => {
      expect(screen.getByText(/message sent successfully/i)).toBeInTheDocument()
    })

    // After reset() is called by the component, the field should be empty
    await waitFor(() => {
      expect((screen.getByLabelText(/name/i) as HTMLInputElement).value).toBe('')
    })
  })
})
