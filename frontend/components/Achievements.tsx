'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { Award, Medal, BadgeCheck } from 'lucide-react'

const awards = [
  {
    title: 'KPMG Megastar Award',
    year: '2024',
    description: 'Exceptional performance and innovation in AI/ML projects',
    icon: Award,
  },
  {
    title: 'KPMG Encore Kudos Award',
    year: '2023',
    description: 'Outstanding contribution to GenAI initiatives',
    icon: Medal,
  },
]

const certifications = [
  {
    title: 'Azure AI Fundamentals (AI-900)',
    issuer: 'Microsoft',
  },
  {
    title: 'Neural Networks and Deep Learning',
    issuer: 'Coursera',
  },
  {
    title: 'Data Scientist Nanodegree',
    issuer: 'Udacity',
  },
  {
    title: 'Improving Deep Neural Networks',
    issuer: 'Coursera',
  },
  {
    title: 'Machine Learning for Business Professionals',
    issuer: 'Coursera',
  },
]

export default function Achievements() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="achievements" className="section-container" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Awards & <span className="gradient-text">Certifications</span>
        </h2>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-12">
        {/* Awards Section */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
            <Award className="w-6 h-6 text-yellow-500" />
            Awards & Recognition
          </h3>
          <div className="space-y-4">
            {awards.map((award, index) => (
              <motion.div
                key={award.title}
                initial={{ opacity: 0, x: -20 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card flex items-start gap-4"
              >
                <div className="flex-shrink-0 p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                  <award.icon className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div>
                  <h4 className="font-bold text-gray-900 dark:text-white">{award.title}</h4>
                  <p className="text-sm text-primary-600 dark:text-primary-400 mb-1">{award.year}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{award.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Certifications Section */}
        <div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
            <BadgeCheck className="w-6 h-6 text-primary-500" />
            Professional Certifications
          </h3>
          <div className="space-y-3">
            {certifications.map((cert, index) => (
              <motion.div
                key={cert.title}
                initial={{ opacity: 0, x: 20 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="card flex items-center gap-4"
              >
                <div className="flex-shrink-0 p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                  <BadgeCheck className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white text-sm">{cert.title}</h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{cert.issuer}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
