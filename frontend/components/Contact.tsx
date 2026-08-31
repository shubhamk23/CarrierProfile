'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail, Send, Loader2, CheckCircle, AlertCircle, MapPin, Phone, Linkedin, Github } from 'lucide-react'
import { submitContactForm } from '@/lib/api'
import { siteConfig } from '@/lib/site-config'

const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
})

type ContactFormData = z.infer<typeof contactSchema>

export default function Contact() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: '-100px' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
  })

  const onSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true)
    setSubmitStatus('idle')

    try {
      await submitContactForm(data)
      setSubmitStatus('success')
      reset()
    } catch (error) {
      console.error('Contact form submission failed:', error)
      setSubmitStatus('error')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section id="contact" className="section-container bg-gray-50 dark:bg-dark-card/50" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <h2 className="section-title">
          Get In <span className="gradient-text">Touch</span>
        </h2>
      </motion.div>

      <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
        {/* Contact Info */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Let&apos;s Connect
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-8">
            I&apos;m always open to discussing new opportunities, interesting projects, or
            collaborations in the AI/ML space. Feel free to reach out!
          </p>

          <div className="space-y-4">
            <a
              href={`mailto:${siteConfig.email}`}
              className="flex items-center gap-4 p-4 rounded-lg bg-white dark:bg-dark-card border border-gray-100 dark:border-dark-border hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
            >
              <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <Mail className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Email</p>
                <p className="font-medium text-gray-900 dark:text-white">{siteConfig.email}</p>
              </div>
            </a>

            <a
              href={siteConfig.phoneHref}
              className="flex items-center gap-4 p-4 rounded-lg bg-white dark:bg-dark-card border border-gray-100 dark:border-dark-border hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
            >
              <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <Phone className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Phone</p>
                <p className="font-medium text-gray-900 dark:text-white">{siteConfig.phone}</p>
              </div>
            </a>

            <div className="flex items-center gap-4 p-4 rounded-lg bg-white dark:bg-dark-card border border-gray-100 dark:border-dark-border">
              <div className="p-3 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
                <MapPin className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Location</p>
                <p className="font-medium text-gray-900 dark:text-white">{siteConfig.location}</p>
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <a
                href={siteConfig.linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-white dark:bg-dark-card border border-gray-100 dark:border-dark-border rounded-lg hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
              >
                <Linkedin className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </a>
              <a
                href={siteConfig.github}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-white dark:bg-dark-card border border-gray-100 dark:border-dark-border rounded-lg hover:border-primary-500 dark:hover:border-primary-500 transition-colors"
              >
                <Github className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </a>
            </div>
          </div>
        </motion.div>

        {/* Contact Form */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="card">
            <div className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  {...register('name')}
                  className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors text-gray-900 dark:text-white"
                  placeholder="Your name"
                />
                {errors.name && (
                  <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  {...register('email')}
                  className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors text-gray-900 dark:text-white"
                  placeholder="your.email@example.com"
                />
                {errors.email && (
                  <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="subject" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Subject
                </label>
                <input
                  type="text"
                  id="subject"
                  {...register('subject')}
                  className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors text-gray-900 dark:text-white"
                  placeholder="What's this about?"
                />
                {errors.subject && (
                  <p className="text-red-500 text-xs mt-1">{errors.subject.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Message
                </label>
                <textarea
                  id="message"
                  rows={4}
                  {...register('message')}
                  className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-dark-border bg-white dark:bg-dark-bg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors resize-none text-gray-900 dark:text-white"
                  placeholder="Your message..."
                />
                {errors.message && (
                  <p className="text-red-500 text-xs mt-1">{errors.message.message}</p>
                )}
              </div>

              {submitStatus === 'success' && (
                <div className="flex items-center gap-2 p-3 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm">Message sent successfully!</span>
                </div>
              )}

              {submitStatus === 'error' && (
                <div className="flex items-center gap-2 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-sm">Failed to send message. Please try again.</span>
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send Message
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </section>
  )
}
