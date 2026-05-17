// Knowledge-hub shared types — kept in sync with backend Pydantic schemas
// (see backend/app/knowledge/schemas.py).

export interface Section {
  id: number
  slug: string
  title: string
  description: string | null
  icon: string | null
  sort_order: number
  note_count: number
}

export interface NoteCard {
  id: number
  slug: string
  section_slug: string
  title: string
  summary: string | null
  tags: string[]
  read_time: number
  level: 'beginner' | 'intermediate' | 'advanced'
  created_at: string
  updated_at: string | null
}

export interface NoteDetail extends NoteCard {
  content: string
  visibility: 'public' | 'draft'
  word_count: number
}

export interface NoteAdmin extends NoteDetail {
  file_path: string
}

export interface SectionPageResponse {
  section: Section
  notes: NoteCard[]
}

export interface SearchResult {
  id: number
  slug: string
  section_slug: string
  title: string
  excerpt: string
  tags: string[]
}

export interface SearchResponse {
  results: SearchResult[]
  total: number
  query: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface KnowledgeHealth {
  status: string
  note_count: number
  section_count: number
}
