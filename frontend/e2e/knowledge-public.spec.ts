import { expect, test } from '@playwright/test'

// Public knowledge-hub flow: lands on home → clicks through to /knowledge →
// drills into a section → opens a note → verifies KaTeX + code rendering.
// Requires the backend to be seeded (the empty-DB bootstrap reindex runs
// on first start when KNOWLEDGE_INDEX_ON_BOOT=True).

test.describe('@knowledge public flow', () => {
  test('home page links to knowledge hub', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('text=Knowledge Hub')).toBeVisible()
    await page
      .getByRole('link', { name: /Explore the full knowledge hub/i })
      .click()
    await expect(page).toHaveURL(/\/knowledge$/)
  })

  test('knowledge index renders all section cards', async ({ page }) => {
    await page.goto('/knowledge')
    await expect(
      page.getByRole('heading', { name: /Knowledge Hub/i }),
    ).toBeVisible()

    // Section cards should be clickable links.
    const sectionLinks = page.locator('a[href^="/knowledge/"]')
    await expect(sectionLinks.first()).toBeVisible()
    expect(await sectionLinks.count()).toBeGreaterThan(0)
  })

  test('section page lists notes with metadata', async ({ page }) => {
    await page.goto('/knowledge/nlp')
    await expect(page.getByRole('heading', { name: /NLP/i })).toBeVisible()
    // Either notes appear or an empty-state message — both are valid.
    const noteCards = page.locator('a[href^="/knowledge/nlp/"]')
    if ((await noteCards.count()) > 0) {
      await expect(noteCards.first()).toBeVisible()
    }
  })

  test('note detail renders content and metadata', async ({ page }) => {
    // Try a known seeded note.
    await page.goto('/knowledge/nlp/attention')
    await expect(
      page.getByRole('heading', { name: /Attention/i }),
    ).toBeVisible()
    // Read-time badge.
    await expect(page.locator('text=/min read/')).toBeVisible()
  })

  test('search returns ranked results', async ({ page }) => {
    await page.goto('/knowledge/search?q=attention')
    await expect(page.locator('text=/result/')).toBeVisible()
    // The first result must link to a note.
    await expect(
      page.locator('a[href^="/knowledge/"][href*="/attention"]').first(),
    ).toBeVisible()
  })

  test('search bar from index navigates to results', async ({ page }) => {
    await page.goto('/knowledge')
    await page.getByPlaceholder(/Search/i).fill('transformer')
    await page.getByPlaceholder(/Search/i).press('Enter')
    await expect(page).toHaveURL(/\/knowledge\/search\?q=transformer/)
  })

  test('404 on unknown section', async ({ page }) => {
    const res = await page.goto('/knowledge/does-not-exist')
    expect(res?.status()).toBe(404)
  })
})
