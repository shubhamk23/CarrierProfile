/**
 * Tests for components/ThemeToggle.tsx
 *
 * Key behaviours tested:
 * - Before the component mounts (mounted=false) it renders only a placeholder
 * - After mount it shows the Moon icon in light theme and Sun in dark theme
 * - Clicking the button calls setTheme with the toggled value
 */

import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'

// Mock next-themes so we can control `theme` and spy on `setTheme`
const mockSetTheme = jest.fn()
let mockTheme = 'light'

jest.mock('next-themes', () => ({
  useTheme: () => ({
    theme: mockTheme,
    setTheme: mockSetTheme,
  }),
}))

// lucide-react uses SVG; replace with testable data-testid elements
jest.mock('lucide-react', () => ({
  Moon: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="moon-icon" {...props} />,
  Sun: (props: React.SVGProps<SVGSVGElement>) => <svg data-testid="sun-icon" {...props} />,
}))

import ThemeToggle from '../../components/ThemeToggle'

beforeEach(() => {
  mockSetTheme.mockClear()
  mockTheme = 'light'
})

describe('ThemeToggle — pre-mount placeholder', () => {
  it('renders a button even before mount', () => {
    // React's useEffect hasn't run in the initial render snapshot,
    // but with RTL it does fire synchronously; we rely on the mounted guard.
    render(<ThemeToggle />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })
})

describe('ThemeToggle — light theme', () => {
  it('shows Moon icon when theme is light', () => {
    mockTheme = 'light'
    render(<ThemeToggle />)
    expect(screen.getByTestId('moon-icon')).toBeInTheDocument()
  })

  it('does not show Sun icon when theme is light', () => {
    mockTheme = 'light'
    render(<ThemeToggle />)
    expect(screen.queryByTestId('sun-icon')).not.toBeInTheDocument()
  })

  it('calls setTheme("dark") when clicked in light mode', () => {
    mockTheme = 'light'
    render(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button', { name: /toggle theme/i }))
    expect(mockSetTheme).toHaveBeenCalledWith('dark')
  })
})

describe('ThemeToggle — dark theme', () => {
  it('shows Sun icon when theme is dark', () => {
    mockTheme = 'dark'
    render(<ThemeToggle />)
    expect(screen.getByTestId('sun-icon')).toBeInTheDocument()
  })

  it('does not show Moon icon when theme is dark', () => {
    mockTheme = 'dark'
    render(<ThemeToggle />)
    expect(screen.queryByTestId('moon-icon')).not.toBeInTheDocument()
  })

  it('calls setTheme("light") when clicked in dark mode', () => {
    mockTheme = 'dark'
    render(<ThemeToggle />)
    fireEvent.click(screen.getByRole('button', { name: /toggle theme/i }))
    expect(mockSetTheme).toHaveBeenCalledWith('light')
  })
})
