'use client'

import { motion } from 'framer-motion'
import { MapPin, Mail, Linkedin, Github, Download, ChevronDown } from 'lucide-react'

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-blue-50 dark:from-dark-bg dark:via-dark-bg dark:to-primary-950/20" />

      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 dark:bg-primary-900/20 rounded-full blur-3xl opacity-50" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200 dark:bg-blue-900/20 rounded-full blur-3xl opacity-50" />
      </div>

      <div className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold mb-4">
            <span className="text-gray-900 dark:text-white">Shubham </span>
            <span className="gradient-text">Khanapure</span>
          </h1>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <p className="text-lg sm:text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-6">
            Senior ML Engineer
          </p>
          <p className="text-base sm:text-lg text-primary-600 dark:text-primary-400 font-medium mb-8">
            Generative AI & Computer Vision Specialist
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex items-center justify-center text-gray-500 dark:text-gray-400 mb-8"
        >
          <MapPin className="w-4 h-4 mr-2" />
          <span>Pune, India</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-wrap items-center justify-center gap-4 mb-12"
        >
          <a
            href="mailto:shubhamkhanapure@gmail.com"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-300 text-gray-700 dark:text-gray-300"
          >
            <Mail className="w-4 h-4" />
            <span className="text-sm">Email</span>
          </a>
          <a
            href="https://www.linkedin.com/in/shubham-khanapure-4191b1127/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-300 text-gray-700 dark:text-gray-300"
          >
            <Linkedin className="w-4 h-4" />
            <span className="text-sm">LinkedIn</span>
          </a>
          <a
            href="https://github.com/shubhamk23"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-100 dark:bg-dark-card hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-300 text-gray-700 dark:text-gray-300"
          >
            <Github className="w-4 h-4" />
            <span className="text-sm">GitHub</span>
          </a>
          <a
            href={process.env.NEXT_PUBLIC_RESUME_URL || "/resume.pdf"}
            download
            className="btn-primary flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Resume</span>
          </a>
        </motion.div>

        <motion.a
          href="#about"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="inline-block animate-bounce"
        >
          <ChevronDown className="w-8 h-8 text-gray-400 dark:text-gray-500" />
        </motion.a>
      </div>
    </section>
  )
}
