'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { Building2, Calendar, ChevronDown, ChevronUp } from 'lucide-react'

const experiences = [
  {
    company: 'Emerson Export Engineering Centre',
    role: 'Data Scientist - Generative AI & Computer Vision',
    location: 'Pune, India',
    period: 'April 2025 - Present',
    description: [
      'Developed production-grade P&ID Functional Specification Generation (FSG) system processing high-resolution complex engineering diagrams using YOLO object detection, Azure Custom Vision, and Azure Document Intelligence.',
      'Architected production-level microservices using Flask deployed on Azure Web Apps serving real-time predictions; integrated with Azure ML Workspace for model versioning and serving.',
      'Built agentic RAG system using LangGraph multi-agent architecture for automated functional specification document generation with Guardrails AI validation.',
    ],
    technologies: ['YOLO', 'Azure ML', 'LangGraph', 'Flask', 'DocTR OCR', 'Guardrails AI'],
  },
  {
    company: 'TEKsystems India (Client: HSBC)',
    role: 'Data Scientist - NLP & Computer Vision',
    location: 'Pune, India',
    period: 'July 2024 - April 2025',
    description: [
      'Implemented NLP and OpenCV solutions for real-time workforce monitoring system processing employee interactions with automated activity classification and tracking.',
      'Built multi-modal OCR pipeline using EAST/CRAFT text detection with Tesseract, PaddleOCR, and DocTR for recognition processing large-scale financial data via PySpark on Azure Databricks.',
      'Built end-to-end CI/CD pipelines using Azure DevOps and Docker containerization with Azure Container Registry.',
    ],
    technologies: ['NLP', 'OpenCV', 'PySpark', 'Azure Databricks', 'Docker', 'Prometheus', 'Grafana'],
  },
  {
    company: 'KPMG Global Services',
    role: 'Associate Consultant - Data Scientist',
    location: 'Pune, India',
    period: 'June 2022 - July 2024',
    description: [
      'Developed and deployed production GenAI applications using GPT-4, Azure OpenAI, and LangChain serving enterprise users; reduced manual business process effort by 70-80%.',
      'Designed enterprise RAG architecture with semantic search using sentence transformers and vector databases (Pinecone, Weaviate).',
      'Performed LLM fine-tuning and optimization using LoRA/QLoRA techniques improving inference efficiency.',
      'Recipient of KPMG Megastar Award and KPMG Encore Kudos Award for exceptional performance.',
    ],
    technologies: ['GPT-4', 'LangChain', 'Azure OpenAI', 'RAG', 'Pinecone', 'MLflow', 'Django', 'FastAPI'],
  },
  {
    company: 'Vyom Labs',
    role: 'Engineer - Data Scientist',
    location: 'Pune, India',
    period: 'September 2019 - May 2022',
    description: [
      'Developed and deployed supervised and unsupervised ML models using PyTorch, scikit-learn, and XGBoost.',
      'Built automated ticket routing system achieving 88% classification accuracy.',
      'Implemented NLP pipelines for text classification and NER using BERT and spaCy achieving high F1-scores.',
      'Built automated data processing pipelines using Apache Airflow with PCA/LDA dimensionality reduction.',
    ],
    technologies: ['PyTorch', 'scikit-learn', 'XGBoost', 'BERT', 'spaCy', 'Apache Airflow'],
  },
]

function ExperienceCard({ experience, index }: { experience: typeof experiences[0]; index: number }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="relative flex items-start gap-6 md:gap-8"
    >
      {/* Timeline dot - positioned on the left line */}
      <div className="absolute left-0 top-6 w-4 h-4 bg-primary-500 rounded-full transform -translate-x-1/2 border-4 border-white dark:border-dark-card/50 z-10 shadow-md" />

      {/* Content card */}
      <div className="ml-6 flex-1">
        <div className="card">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
              <Building2 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                {experience.company}
              </h3>
              <p className="text-primary-600 dark:text-primary-400 font-medium mb-2">
                {experience.role}
              </p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-4">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {experience.period}
                </span>
                <span>{experience.location}</span>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <ul className={`space-y-2 text-gray-600 dark:text-gray-300 text-sm ${isExpanded ? '' : 'line-clamp-3'}`}>
              {experience.description.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>

            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-3 text-primary-600 dark:text-primary-400 text-sm font-medium flex items-center gap-1 hover:underline"
            >
              {isExpanded ? (
                <>
                  Show Less <ChevronUp className="w-4 h-4" />
                </>
              ) : (
                <>
                  Show More <ChevronDown className="w-4 h-4" />
                </>
              )}
            </button>

            <div className="flex flex-wrap gap-2 mt-4">
              {experience.technologies.map((tech) => (
                <span key={tech} className="skill-badge text-xs">
                  {tech}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default function Experience() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="experience" className="section-container bg-gray-50 dark:bg-dark-card/50" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Work <span className="gradient-text">Experience</span>
        </h2>
      </motion.div>

      <div className="relative max-w-4xl mx-auto">
        {/* Timeline line - vertical line on the left */}
        <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary-200 dark:bg-primary-800" />

        <div className="space-y-8 pl-2">
          {experiences.map((experience, index) => (
            <ExperienceCard key={experience.company} experience={experience} index={index} />
          ))}
        </div>
      </div>
    </section>
  )
}
