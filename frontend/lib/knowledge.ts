// Knowledge-hub API client. Server Components and Client Components both
// import from here. Authenticated calls accept an explicit token argument so
// they're explicit about boundaries.

import type {
  NoteAdmin,
  NoteDetail,
  Section,
  SearchResponse,
  SectionPageResponse,
  TokenResponse,
} from '@/types/knowledge'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''
const KNOWLEDGE = `${API_BASE_URL}/api/knowledge`

// Revalidate cached server-side fetches every 60 seconds in production.
const DEFAULT_REVALIDATE = 60

async function jsonFetch<T>(
  path: string,
  init: RequestInit & { revalidate?: number | false } = {},
): Promise<T> {
  const { revalidate = DEFAULT_REVALIDATE, ...rest } = init
  const next =
    revalidate === false
      ? { cache: 'no-store' as const }
      : { next: { revalidate } }

  const res = await fetch(`${KNOWLEDGE}${path}`, {
    ...next,
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(rest.headers || {}),
    },
  })

  if (!res.ok) {
    const message = await res.text().catch(() => res.statusText)
    throw new KnowledgeApiError(res.status, message || `HTTP ${res.status}`)
  }

  return res.json() as Promise<T>
}

export class KnowledgeApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'KnowledgeApiError'
  }
}

// ── Public read endpoints ────────────────────────────────────────────────────

export async function listSections(): Promise<Section[]> {
  return jsonFetch<Section[]>('/sections')
}

export async function getSection(slug: string): Promise<SectionPageResponse> {
  return jsonFetch<SectionPageResponse>(
    `/sections/${encodeURIComponent(slug)}`,
  )
}

export async function getNote(
  sectionSlug: string,
  noteSlug: string,
): Promise<NoteDetail> {
  return jsonFetch<NoteDetail>(
    `/notes/${encodeURIComponent(sectionSlug)}/${encodeURIComponent(noteSlug)}`,
  )
}

export async function searchKnowledge(
  query: string,
  options: { limit?: number; offset?: number } = {},
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query })
  if (options.limit) params.set('limit', String(options.limit))
  if (options.offset) params.set('offset', String(options.offset))
  return jsonFetch<SearchResponse>(`/search?${params.toString()}`, {
    revalidate: false,
  })
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  return jsonFetch<TokenResponse>('/auth/token', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    revalidate: false,
  })
}

// ── Admin (requires bearer token) ────────────────────────────────────────────

const authHeader = (token: string) => ({ Authorization: `Bearer ${token}` })

export async function listAllNotes(token: string): Promise<NoteAdmin[]> {
  return jsonFetch<NoteAdmin[]>('/admin/notes', {
    headers: authHeader(token),
    revalidate: false,
  })
}

export async function getAdminNote(
  id: number,
  token: string,
): Promise<NoteAdmin> {
  return jsonFetch<NoteAdmin>(`/admin/notes/${id}`, {
    headers: authHeader(token),
    revalidate: false,
  })
}

export async function updateAdminNote(
  id: number,
  patch: Partial<{
    title: string
    section_slug: string
    content: string
    tags: string[]
    visibility: 'public' | 'draft'
    level: 'beginner' | 'intermediate' | 'advanced'
    slug: string
  }>,
  token: string,
): Promise<NoteAdmin> {
  return jsonFetch<NoteAdmin>(`/admin/notes/${id}`, {
    method: 'PUT',
    headers: authHeader(token),
    body: JSON.stringify(patch),
    revalidate: false,
  })
}

export async function deleteAdminNote(
  id: number,
  token: string,
): Promise<{ deleted: boolean }> {
  return jsonFetch<{ deleted: boolean }>(`/admin/notes/${id}`, {
    method: 'DELETE',
    headers: authHeader(token),
    revalidate: false,
  })
}

export async function reindex(
  token: string,
): Promise<{ indexed: number; errors: string[] }> {
  return jsonFetch<{ indexed: number; errors: string[] }>(
    '/admin/reindex',
    {
      method: 'POST',
      headers: authHeader(token),
      revalidate: false,
    },
  )
}
