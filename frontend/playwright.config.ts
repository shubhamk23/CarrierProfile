import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright config for end-to-end coverage of the knowledge hub.
 *
 * The default project boots a real `next dev` server against the local
 * backend. CI overrides `BASE_URL` and `BACKEND_URL` to point at a preview
 * deployment instead of spawning the dev server.
 */

const BASE_URL = process.env.E2E_BASE_URL ?? 'http://127.0.0.1:3000'
const BACKEND_URL = process.env.E2E_BACKEND_URL ?? 'http://127.0.0.1:8000'

export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? [['github'], ['list']] : 'list',

  use: {
    baseURL: BASE_URL,
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    extraHTTPHeaders: {
      'x-e2e-backend-url': BACKEND_URL,
    },
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Spawn `next dev` automatically when running locally. Skip when CI
  // points us at a preview deployment.
  webServer: process.env.E2E_SKIP_WEB_SERVER
    ? undefined
    : {
        command: `NEXT_PUBLIC_API_URL=${BACKEND_URL} npm run dev`,
        url: BASE_URL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
})
