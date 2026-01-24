import type { Metadata } from 'next'
import './globals.css'
import { ThemeProvider } from '@/components/ThemeProvider'
import Navigation from '@/components/Navigation'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_BASE_URL || 'https://carrier-profile.vercel.app'),
  title: 'Shubham Khanapure | Senior ML Engineer',
  description: 'Senior ML Engineer specializing in Generative AI & Computer Vision. 6+ years of experience building production AI/ML systems at scale.',
  keywords: ['Machine Learning', 'AI', 'Generative AI', 'Computer Vision', 'Python', 'MLOps', 'Data Scientist'],
  authors: [{ name: 'Shubham Khanapure' }],
  openGraph: {
    title: 'Shubham Khanapure | Senior ML Engineer',
    description: 'Senior ML Engineer specializing in Generative AI & Computer Vision',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <Navigation />
          <main>{children}</main>
        </ThemeProvider>
      </body>
    </html>
  )
}
