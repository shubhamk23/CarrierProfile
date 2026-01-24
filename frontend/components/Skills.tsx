'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import { Code, Brain, Eye, Sparkles, Settings, Cloud, Server } from 'lucide-react'

const skillCategories = [
  {
    name: 'Languages',
    icon: Code,
    skills: ['Python', 'SQL', 'JavaScript', 'Bash', 'Java'],
    color: 'from-blue-500 to-cyan-500',
  },
  {
    name: 'ML/DL Frameworks',
    icon: Brain,
    skills: ['PyTorch', 'TensorFlow', 'Keras', 'Scikit-learn', 'XGBoost', 'Hugging Face Transformers'],
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Computer Vision',
    icon: Eye,
    skills: ['YOLO (v5/v8/v11)', 'Faster R-CNN', 'Azure Custom Vision', 'OpenCV', 'SAHI', 'Detectron2', 'Image Segmentation', 'OCR (DocTR, Tesseract, PaddleOCR)'],
    color: 'from-green-500 to-emerald-500',
  },
  {
    name: 'Generative AI & NLP',
    icon: Sparkles,
    skills: ['LangChain', 'LangGraph', 'LlamaIndex', 'GPT-4', 'Azure OpenAI', 'RAG', 'Guardrails AI', 'BERT', 'spaCy', 'NLTK'],
    color: 'from-orange-500 to-red-500',
  },
  {
    name: 'MLOps & DevOps',
    icon: Settings,
    skills: ['Azure ML Studio', 'MLflow', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Model Serving', 'A/B Testing', 'Git'],
    color: 'from-indigo-500 to-violet-500',
  },
  {
    name: 'Cloud & Data',
    icon: Cloud,
    skills: ['Azure (ML Workspace, Databricks, Cognitive Services)', 'Azure DevOps', 'Azure Web Apps', 'Blob Storage', 'PostgreSQL', 'MySQL', 'MongoDB', 'Vector DBs (Pinecone, ChromaDB, Weaviate)'],
    color: 'from-sky-500 to-blue-500',
  },
  {
    name: 'Software Engineering',
    icon: Server,
    skills: ['RESTful APIs', 'Flask', 'FastAPI', 'Django', 'Microservices', 'System Design', 'Agile/Scrum', 'Distributed Systems'],
    color: 'from-teal-500 to-green-500',
  },
]

function SkillCard({ category, index }: { category: typeof skillCategories[0]; index: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-50px' })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="card group hover:scale-105"
    >
      <div className={`inline-flex p-3 rounded-lg bg-gradient-to-r ${category.color} mb-4`}>
        <category.icon className="w-6 h-6 text-white" />
      </div>
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
        {category.name}
      </h3>
      <div className="flex flex-wrap gap-2">
        {category.skills.map((skill) => (
          <span
            key={skill}
            className="px-2 py-1 bg-gray-100 dark:bg-dark-border text-gray-700 dark:text-gray-300 rounded text-xs font-medium"
          >
            {skill}
          </span>
        ))}
      </div>
    </motion.div>
  )
}

export default function Skills() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })

  return (
    <section id="skills" className="section-container" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Technical <span className="gradient-text">Skills</span>
        </h2>
      </motion.div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {skillCategories.map((category, index) => (
          <SkillCard key={category.name} category={category} index={index} />
        ))}
      </div>
    </section>
  )
}
