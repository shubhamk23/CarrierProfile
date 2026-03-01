/**
 * Tests for components/Navigation.tsx
 *
 * Behaviours tested:
 * - Renders the SK logo link
 * - Renders all six nav items in the desktop menu
 * - Mobile menu is hidden by default
 * - Hamburger button toggles the mobile menu open / closed
 * - Clicking a mobile nav link closes the menu
 * - Scroll past 50px changes the nav's className (backdrop-blur)
 */

import React from 'react'
import { render, screen, fireEvent, act } from '@testing-library/react'

// Stub out ThemeToggle so we don't need next-themes in these tests
jest.mock('../../components/ThemeToggle', () => () => <div data-testid="theme-toggle" />)

// Stub lucide-react icons used by Navigation
jest.mock('lucide-react', () => ({
  Menu: () => <svg data-testid="menu-icon" />,
  X: () => <svg data-testid="x-icon" />,
}))

import Navigation from '../../components/Navigation'

const NAV_ITEMS = ['About', 'Experience', 'Skills', 'Projects', 'Achievements', 'Contact']

describe('Navigation — static render', () => {
  it('renders the SK logo', () => {
    render(<Navigation />)
    expect(screen.getByText('SK')).toBeInTheDocument()
  })

  it('renders all six nav items in the desktop nav', () => {
    render(<Navigation />)
    for (const item of NAV_ITEMS) {
      // Multiple elements may be rendered (desktop + mobile), getAllByText is fine
      const links = screen.getAllByText(item)
      expect(links.length).toBeGreaterThan(0)
    }
  })

  it('renders the theme toggle', () => {
    render(<Navigation />)
    expect(screen.getAllByTestId('theme-toggle').length).toBeGreaterThan(0)
  })
})

describe('Navigation — mobile menu', () => {
  it('mobile menu items are not visible by default', () => {
    render(<Navigation />)
    // The mobile nav section only appears when isMobileMenuOpen is true.
    // We assert the hamburger icon is visible (menu closed state).
    expect(screen.getByTestId('menu-icon')).toBeInTheDocument()
    expect(screen.queryByTestId('x-icon')).not.toBeInTheDocument()
  })

  it('opens mobile menu on hamburger click', () => {
    render(<Navigation />)
    const hamburger = screen.getByTestId('menu-icon').closest('button')!
    fireEvent.click(hamburger)
    expect(screen.getByTestId('x-icon')).toBeInTheDocument()
  })

  it('closes mobile menu when hamburger clicked again', () => {
    render(<Navigation />)
    const hamburger = screen.getByTestId('menu-icon').closest('button')!
    fireEvent.click(hamburger) // open
    const closeBtn = screen.getByTestId('x-icon').closest('button')!
    fireEvent.click(closeBtn) // close
    expect(screen.getByTestId('menu-icon')).toBeInTheDocument()
    expect(screen.queryByTestId('x-icon')).not.toBeInTheDocument()
  })

  it('closes mobile menu when a nav link is clicked', () => {
    render(<Navigation />)
    // Open mobile menu
    fireEvent.click(screen.getByTestId('menu-icon').closest('button')!)
    expect(screen.getByTestId('x-icon')).toBeInTheDocument()

    // Click the first mobile nav link (they appear as anchors after menu opens)
    const mobileAboutLinks = screen.getAllByText('About')
    // The second occurrence belongs to the mobile nav (rendered when open)
    fireEvent.click(mobileAboutLinks[mobileAboutLinks.length - 1])

    // Menu should now be closed
    expect(screen.queryByTestId('x-icon')).not.toBeInTheDocument()
  })
})

describe('Navigation — scroll behaviour', () => {
  it('applies backdrop-blur class after scrolling past 50px', () => {
    render(<Navigation />)
    const nav = screen.getByRole('navigation')

    // Initial state — no scroll effect
    expect(nav.className).not.toContain('backdrop-blur-md')

    act(() => {
      // Simulate scroll event
      Object.defineProperty(window, 'scrollY', { value: 60, writable: true })
      window.dispatchEvent(new Event('scroll'))
    })

    expect(nav.className).toContain('backdrop-blur-md')
  })

  it('removes backdrop-blur class when scrolled back to top', () => {
    render(<Navigation />)
    const nav = screen.getByRole('navigation')

    act(() => {
      Object.defineProperty(window, 'scrollY', { value: 60, writable: true })
      window.dispatchEvent(new Event('scroll'))
    })

    expect(nav.className).toContain('backdrop-blur-md')

    act(() => {
      Object.defineProperty(window, 'scrollY', { value: 0, writable: true })
      window.dispatchEvent(new Event('scroll'))
    })

    expect(nav.className).not.toContain('backdrop-blur-md')
  })
})
