'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import rehypeSlug from 'rehype-slug'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import {
  oneDark,
  oneLight,
} from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useTheme } from 'next-themes'
import 'katex/dist/katex.min.css'

interface Props {
  content: string
}

export default function NoteRenderer({ content }: Props) {
  const { resolvedTheme } = useTheme()
  const codeStyle = resolvedTheme === 'dark' ? oneDark : oneLight

  return (
    <div className="prose prose-slate dark:prose-invert max-w-none prose-headings:scroll-mt-24 prose-pre:bg-transparent prose-pre:p-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[
          rehypeKatex,
          rehypeSlug,
          [rehypeAutolinkHeadings, { behavior: 'wrap' }],
        ]}
        components={{
          code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '')
            if (!inline && match) {
              return (
                <SyntaxHighlighter
                  PreTag="div"
                  language={match[1]}
                  style={codeStyle as any}
                  customStyle={{
                    margin: 0,
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                  }}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              )
            }
            return (
              <code
                className="bg-gray-100 dark:bg-dark-card px-1.5 py-0.5 rounded text-sm"
                {...props}
              >
                {children}
              </code>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
