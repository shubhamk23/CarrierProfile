const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Path to your Next.js app directory
  dir: './',
})

/** @type {import('jest').Config} */
const customConfig = {
  testEnvironment: 'jest-environment-jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testMatch: [
    '**/__tests__/**/*.(test|spec).[jt]s?(x)',
    '**/?(*.)+(test|spec).[jt]s?(x)',
  ],
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  // Baseline floor as of the API-surface cleanup, not an aspirational
  // target -- the untested presentational components (About, Hero, Skills,
  // etc.) still need coverage to reach the project's 80% standard.
  coverageThreshold: {
    global: {
      statements: 55,
      branches: 45,
      functions: 50,
      lines: 55,
    },
  },
}

module.exports = createJestConfig(customConfig)
