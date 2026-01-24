'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { GraduationCap, Calendar, MapPin } from 'lucide-react'

export default function Education() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="education" className="section-container bg-gray-50 dark:bg-dark-card/50" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          <span className="gradient-text">Education</span>
        </h2>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="max-w-2xl mx-auto"
      >
        <div className="card">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 p-4 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
              <GraduationCap className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Bachelor of Engineering in Computer Science
              </h3>
              <p className="text-primary-600 dark:text-primary-400 font-medium mb-4">
                Vidya Pratishthan's Kamalnayan Bajaj Institute of Engineering & Technology
              </p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  August 2015 - June 2019
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  Pune, India
                </span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  )
}
