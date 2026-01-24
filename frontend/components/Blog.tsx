'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { BookOpen, Calendar, ArrowRight, Clock } from 'lucide-react'

const blogPosts = [
  {
    title: 'Building Production-Grade RAG Systems with LangChain',
    excerpt: 'A comprehensive guide to architecting and deploying RAG systems for enterprise applications, covering vector databases, retrieval strategies, and evaluation metrics.',
    date: '2024-12-15',
    readTime: '12 min read',
    category: 'Generative AI',
    slug: 'building-production-rag-systems',
  },
  {
    title: 'YOLO Object Detection: From v5 to v11',
    excerpt: 'Exploring the evolution of YOLO models and practical tips for training custom object detection models for industrial applications.',
    date: '2024-11-20',
    readTime: '10 min read',
    category: 'Computer Vision',
    slug: 'yolo-object-detection-evolution',
  },
  {
    title: 'MLOps Best Practices with Azure ML Studio',
    excerpt: 'Learn how to set up end-to-end MLOps pipelines using Azure ML Studio, including experiment tracking, model versioning, and automated deployments.',
    date: '2024-10-05',
    readTime: '15 min read',
    category: 'MLOps',
    slug: 'mlops-azure-ml-studio',
  },
]

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function Blog() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="blog" className="section-container" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Latest <span className="gradient-text">Articles</span>
        </h2>
      </motion.div>

      <div className="grid md:grid-cols-3 gap-6">
        {blogPosts.map((post, index) => (
          <motion.article
            key={post.slug}
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            className="card group cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-4">
              <span className="skill-badge text-xs">{post.category}</span>
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
              {post.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
              {post.excerpt}
            </p>
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {formatDate(post.date)}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {post.readTime}
              </span>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100 dark:border-dark-border">
              <a
                href={`/blog/${post.slug}`}
                className="text-primary-600 dark:text-primary-400 text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all"
              >
                Read More <ArrowRight className="w-4 h-4" />
              </a>
            </div>
          </motion.article>
        ))}
      </div>
    </section>
  )
}
