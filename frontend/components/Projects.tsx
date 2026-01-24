'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { Calendar, ExternalLink, ChevronDown, ChevronUp, Folder } from 'lucide-react'

const projects = [
  {
    title: 'P&ID Functional Specification Generation (FSG)',
    period: 'April 2025 - Present',
    technologies: ['Azure ML', 'YOLO', 'Computer Vision', 'DocTR OCR', 'Flask', 'LangGraph'],
    description: 'Built end-to-end production ML system for automated functional specification generation from high-resolution P&ID engineering diagrams.',
    highlights: [
      'Implemented object detection using YOLO models and Azure Custom Vision with Azure ML Studio data labeling',
      'Text extraction using Azure Document Intelligence and DocTR OCR',
      'Intelligent object-to-tag spatial mapping algorithms for accurate relationship identification',
      'Deployed Flask microservice on Azure Web Apps integrated with Azure ML Workspace',
      'Established complete MLOps pipeline with Azure Job creation, MLflow experiment tracking',
    ],
  },
  {
    title: 'Pulse Intelligence Tool',
    period: 'July 2024',
    technologies: ['Python', 'Deep Learning', 'NLP', 'OpenCV', 'Azure', 'Databricks'],
    description: 'Implemented LLM-powered workforce management tool with machine learning and automation.',
    highlights: [
      'Developed end-to-end monitoring system tracking user activities on whitelisted applications',
      'Automated pipeline from logging to report generation',
      'Visualization dashboards supporting multiple concurrent users',
    ],
  },
  {
    title: 'CSRD and SEC Readiness Assessment Tool',
    period: 'December 2023',
    technologies: ['Python', 'NLP', 'GenAI', 'Azure OpenAI', 'RAG'],
    description: 'Developed LLM-powered compliance assessment system reducing manual effort by 70-80%.',
    highlights: [
      'Implemented end-to-end pipeline from disclosure requirements to report generation',
      'Automated question generation and RAG system for answering',
      'AI-powered evaluation for compliance assessment',
    ],
  },
  {
    title: 'Job Architecture Optimization',
    period: 'December 2023',
    technologies: ['Python', 'NLP', 'GenAI', 'Prompt Engineering', 'Django', 'Azure'],
    description: 'Implemented GenAI solution for job architecture optimization classifying families and groups.',
    highlights: [
      'Developed decision tree for career path determination',
      'Created Django application deployed on Azure Web Service',
      'Production-grade scalability for enterprise use',
    ],
  },
  {
    title: 'Intelligence RFP Builder',
    period: 'January 2023',
    technologies: ['Python', 'NLP', 'Hugging Face', 'PyTorch', 'Django', 'Azure', 'Docker'],
    description: 'Built automated RFP response system with semantic search and sentence similarity matching.',
    highlights: [
      'Extracted questions from documents and generated responses',
      'Integrated GPT-4 chatbot for interactive assistance',
      'Deployed complete Django web application on Azure using Docker',
    ],
  },
  {
    title: 'Ticket Classification & Entity Extraction',
    period: 'January 2020',
    technologies: ['Python', 'ML', 'NLP', 'Azure', 'BERT', 'spaCy'],
    description: 'Built machine learning model for automated ticket routing analyzing mail text and assigning to departments.',
    highlights: [
      'Achieved 88% classification accuracy',
      'Improved efficiency and reduced resolution time',
      'Implemented NLP pipelines for text classification and NER',
    ],
  },
]

function ProjectCard({ project, index }: { project: typeof projects[0]; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="card"
    >
      <div className="flex items-start gap-4 mb-4">
        <div className="flex-shrink-0 p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
          <Folder className="w-6 h-6 text-primary-600 dark:text-primary-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
            {project.title}
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
            <Calendar className="w-4 h-4" />
            {project.period}
          </div>
        </div>
      </div>

      <p className="text-gray-600 dark:text-gray-300 mb-4">
        {project.description}
      </p>

      {isExpanded && (
        <motion.ul
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="list-disc list-inside space-y-2 text-sm text-gray-600 dark:text-gray-300 mb-4"
        >
          {project.highlights.map((highlight, i) => (
            <li key={i}>{highlight}</li>
          ))}
        </motion.ul>
      )}

      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-primary-600 dark:text-primary-400 text-sm font-medium flex items-center gap-1 hover:underline mb-4"
      >
        {isExpanded ? (
          <>
            Show Less <ChevronUp className="w-4 h-4" />
          </>
        ) : (
          <>
            Show Details <ChevronDown className="w-4 h-4" />
          </>
        )}
      </button>

      <div className="flex flex-wrap gap-2">
        {project.technologies.map((tech) => (
          <span key={tech} className="skill-badge text-xs">
            {tech}
          </span>
        ))}
      </div>
    </motion.div>
  )
}

export default function Projects() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="projects" className="section-container bg-gray-50 dark:bg-dark-card/50" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Key <span className="gradient-text">Projects</span>
        </h2>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-6">
        {projects.map((project, index) => (
          <ProjectCard key={project.title} project={project} index={index} />
        ))}
      </div>
    </section>
  )
}
