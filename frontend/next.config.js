/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  images: {
    domains: ['supabase.co'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
      },
    ],
  },

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              // Next.js needs unsafe-inline/eval for hydration; KaTeX needs them too.
              "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
              // KaTeX ships inline styles; bundled CSS is served from /_next.
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: https://*.supabase.co",
              // Allow the knowledge backend on any *.vercel.app preview/prod.
              "connect-src 'self' https://*.vercel.app https://*.supabase.co",
              // KaTeX fonts ship as base64 data URIs via the bundled CSS — data: needed.
              "font-src 'self' data:",
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
              "frame-ancestors 'none'",
              'upgrade-insecure-requests',
            ].join('; '),
          },
        ],
      },
    ]
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
