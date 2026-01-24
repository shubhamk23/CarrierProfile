'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { Briefcase, Code, Award, Rocket } from 'lucide-react'

const stats = [
  { icon: Briefcase, value: '6+', label: 'Years Experience' },
  { icon: Code, value: '10+', label: 'Production Systems' },
  { icon: Award, value: '2', label: 'KPMG Awards' },
  { icon: Rocket, value: '70-80%', label: 'Efficiency Gains' },
]

export default function About() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="about" className="section-container" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          About <span className="gradient-text">Me</span>
        </h2>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
            Senior ML Engineer with <span className="font-semibold text-primary-600 dark:text-primary-400">6+ years</span> building
            production AI/ML systems at scale. Specialized in{' '}
            <span className="font-semibold text-primary-600 dark:text-primary-400">Generative AI</span> (LangChain,
            agentic RAG, LLMs) and{' '}
            <span className="font-semibold text-primary-600 dark:text-primary-400">Computer Vision</span> (YOLO,
            object detection, OCR).
          </p>
          <p className="text-lg text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
            Expert in Python, PyTorch, Azure ML, end-to-end MLOps pipelines, and distributed systems.
            Proven track record of reducing manual effort by 70-80% through AI automation, developing
            enterprise-scale GenAI applications, and delivering scalable production solutions in
            financial services and engineering automation domains.
          </p>
          <div className="flex flex-wrap gap-2">
            {['Generative AI', 'Computer Vision', 'MLOps', 'Python', 'Azure'].map((tag) => (
              <span key={tag} className="skill-badge">
                {tag}
              </span>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-2 gap-4"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              className="card text-center"
            >
              <stat.icon className="w-8 h-8 mx-auto mb-3 text-primary-500" />
              <div className="text-3xl font-bold gradient-text mb-1">{stat.value}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
