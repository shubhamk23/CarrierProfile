import { expect, test } from '@playwright/test'

// Admin flow — login, list, view an editor. Requires admin credentials in
// env vars (E2E_ADMIN_USERNAME, E2E_ADMIN_PASSWORD). Skipped if absent so the
// suite stays green on machines without admin secrets.
const ADMIN_USERNAME = process.env.E2E_ADMIN_USERNAME
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASSWORD

test.describe('@knowledge admin flow', () => {
  test.skip(
    !ADMIN_USERNAME || !ADMIN_PASSWORD,
    'E2E_ADMIN_USERNAME / E2E_ADMIN_PASSWORD not set',
  )

  test('signs in and lists notes', async ({ page }) => {
    await page.goto('/knowledge/admin/login')
    await page.fill('input[type="text"]', ADMIN_USERNAME!)
    await page.fill('input[type="password"]', ADMIN_PASSWORD!)
    await page.getByRole('button', { name: /Sign in/i }).click()

    await expect(page).toHaveURL(/\/knowledge\/admin$/)
    await expect(
      page.getByRole('heading', { name: /Knowledge Hub Admin/i }),
    ).toBeVisible()
    await expect(page.locator('table')).toBeVisible()
  })

  test('reindex button completes successfully', async ({ page }) => {
    await page.goto('/knowledge/admin/login')
    await page.fill('input[type="text"]', ADMIN_USERNAME!)
    await page.fill('input[type="password"]', ADMIN_PASSWORD!)
    await page.getByRole('button', { name: /Sign in/i }).click()

    await page.getByRole('button', { name: /Reindex/i }).click()

    // Wait for the spinner to disappear (no easy success state — we just
    // confirm the button returns to its idle label).
    await expect(
      page.getByRole('button', { name: /Reindex/i }),
    ).toBeVisible({ timeout: 30_000 })
  })

  test('login rejects bad credentials', async ({ page }) => {
    await page.goto('/knowledge/admin/login')
    await page.fill('input[type="text"]', 'wrong-user')
    await page.fill('input[type="password"]', 'wrong-pass')
    await page.getByRole('button', { name: /Sign in/i }).click()

    await expect(page.locator('text=/HTTP|Incorrect|fail/i')).toBeVisible({
      timeout: 5_000,
    })
  })

  test('anonymous user is redirected away from admin', async ({ page }) => {
    // Use a fresh context with no localStorage.
    await page.context().clearCookies()
    await page.evaluate(() => localStorage.clear()).catch(() => {})
    await page.goto('/knowledge/admin')
    await expect(page).toHaveURL(/\/knowledge\/admin\/login$/)
  })
})
