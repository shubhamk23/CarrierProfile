import { expect, test } from '@playwright/test'

// Portfolio regression suite — the migration must not break existing surfaces.
test.describe('@portfolio regression', () => {
  test('home page renders all primary sections', async ({ page }) => {
    await page.goto('/')

    // Hero + a sampling of the home sections must render.
    await expect(page.locator('#about, [id="about"]')).toBeVisible()
    await expect(page.locator('#experience, [id="experience"]')).toBeVisible()
    await expect(page.locator('#contact, [id="contact"]')).toBeVisible()
  })

  test('top nav has a Knowledge link', async ({ page }) => {
    await page.goto('/')
    await expect(
      page.getByRole('link', { name: 'Knowledge' }).first(),
    ).toBeVisible()
  })

  test('theme toggle persists across navigation', async ({ page }) => {
    await page.goto('/')
    // Try a few common toggle selectors.
    const toggle = page
      .getByRole('button', { name: /theme|dark|light/i })
      .first()
    if (await toggle.isVisible().catch(() => false)) {
      const initialClass = await page
        .locator('html')
        .getAttribute('class')
        .then((c) => c ?? '')
      await toggle.click()
      // Allow next-themes to write into <html>.
      await page.waitForTimeout(200)
      const newClass = await page
        .locator('html')
        .getAttribute('class')
        .then((c) => c ?? '')
      expect(newClass).not.toBe(initialClass)

      // Navigate to /knowledge — the toggled theme should persist.
      await page.getByRole('link', { name: 'Knowledge' }).first().click()
      await expect(page).toHaveURL(/\/knowledge$/)
      const knowledgeClass = await page
        .locator('html')
        .getAttribute('class')
        .then((c) => c ?? '')
      expect(knowledgeClass).toBe(newClass)
    }
  })

  test('contact form is reachable', async ({ page }) => {
    await page.goto('/#contact')
    await expect(page.locator('input[name="name"], input#name')).toBeVisible({
      timeout: 5_000,
    })
  })

  test('sitemap exposes both portfolio and knowledge URLs', async ({
    request,
  }) => {
    const res = await request.get('/sitemap.xml')
    expect(res.status()).toBe(200)
    const body = await res.text()
    expect(body).toContain('/knowledge')
  })

  test('robots disallows admin', async ({ request }) => {
    const res = await request.get('/robots.txt')
    expect(res.status()).toBe(200)
    expect(await res.text()).toContain('/knowledge/admin')
  })
})
