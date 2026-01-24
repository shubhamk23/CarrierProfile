'use client'

import { useParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Calendar, Clock, Tag } from 'lucide-react'
import Link from 'next/link'

// Sample blog posts data (same as in Blog component)
const blogPosts: Record<string, {
  title: string
  excerpt: string
  date: string
  readTime: string
  category: string
  content: string
}> = {
  'building-production-rag-systems': {
    title: 'Building Production-Grade RAG Systems with LangChain',
    excerpt: 'A comprehensive guide to architecting and deploying RAG systems for enterprise applications.',
    date: '2024-12-15',
    readTime: '12 min read',
    category: 'Generative AI',
    content: `
# Building Production-Grade RAG Systems with LangChain

Retrieval-Augmented Generation (RAG) has become the de facto approach for building LLM applications that need to work with private or domain-specific data. In this article, I'll share my experience building production RAG systems at scale.

## Architecture Overview

A production RAG system typically consists of:

1. **Document Processing Pipeline** - Chunking, embedding, and indexing documents
2. **Vector Store** - Storing and retrieving embeddings efficiently
3. **Retrieval Layer** - Finding relevant documents for a query
4. **Generation Layer** - Using LLM to generate responses

## Key Considerations

### Chunking Strategy

The way you split documents significantly impacts retrieval quality. Consider:
- Semantic chunking over fixed-size chunks
- Overlap between chunks to maintain context
- Metadata preservation for filtering

### Vector Database Selection

For production systems, consider:
- **Pinecone** - Managed, scalable, easy to use
- **Weaviate** - Open source with hybrid search
- **ChromaDB** - Great for development and small-scale

### Evaluation

Implement metrics like:
- Retrieval precision and recall
- Answer relevance scores
- Hallucination detection

## Conclusion

Building production RAG systems requires careful attention to architecture, chunking strategies, and evaluation. Start simple, measure everything, and iterate based on real-world performance.
    `,
  },
  'yolo-object-detection-evolution': {
    title: 'YOLO Object Detection: From v5 to v11',
    excerpt: 'Exploring the evolution of YOLO models and practical tips for training custom object detection models.',
    date: '2024-11-20',
    readTime: '10 min read',
    category: 'Computer Vision',
    content: `
# YOLO Object Detection: From v5 to v11

YOLO (You Only Look Once) has revolutionized real-time object detection. Let me share my experience working with different YOLO versions in production.

## Evolution of YOLO

### YOLOv5
- PyTorch-based implementation
- Easy to train and deploy
- Great community support

### YOLOv8
- Improved architecture
- Better accuracy-speed tradeoff
- Built-in tracking support

### YOLOv11
- Latest improvements
- Enhanced small object detection
- Better handling of complex scenes

## Training Tips

1. **Data Quality** - Clean, well-annotated data is crucial
2. **Augmentation** - Use appropriate augmentation for your domain
3. **Hyperparameter Tuning** - Start with defaults, then fine-tune
4. **Validation Strategy** - Ensure your validation set represents production data

## Deployment Considerations

- Model quantization for edge deployment
- Batch inference for throughput
- TensorRT optimization for NVIDIA GPUs

## Conclusion

Choose your YOLO version based on your specific requirements. v8 offers the best balance for most applications, while v11 is ideal for cutting-edge performance.
    `,
  },
  'mlops-azure-ml-studio': {
    title: 'MLOps Best Practices with Azure ML Studio',
    excerpt: 'Learn how to set up end-to-end MLOps pipelines using Azure ML Studio.',
    date: '2024-10-05',
    readTime: '15 min read',
    category: 'MLOps',
    content: `
# MLOps Best Practices with Azure ML Studio

Setting up robust MLOps pipelines is crucial for production ML systems. Here's how to leverage Azure ML Studio effectively.

## Key Components

### Experiment Tracking
- Use MLflow integration for tracking
- Log metrics, parameters, and artifacts
- Compare runs systematically

### Model Registry
- Version all models
- Track model lineage
- Implement approval workflows

### Automated Pipelines
- Define training pipelines as code
- Schedule retraining jobs
- Implement CI/CD for ML

## Best Practices

1. **Infrastructure as Code** - Define everything in ARM templates or Terraform
2. **Reproducibility** - Pin all dependencies, use containers
3. **Monitoring** - Track model performance in production
4. **Cost Management** - Use spot instances, auto-scaling

## Sample Pipeline Structure

\`\`\`python
from azure.ai.ml import MLClient
from azure.ai.ml.dsl import pipeline

@pipeline
def training_pipeline(data_path):
    preprocess = preprocess_component(data=data_path)
    train = train_component(data=preprocess.outputs.output)
    evaluate = evaluate_component(model=train.outputs.model)
    return evaluate.outputs
\`\`\`

## Conclusion

Azure ML Studio provides all the tools needed for production MLOps. Start with the basics and gradually add complexity as your needs grow.
    `,
  },
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function BlogPostPage() {
  const params = useParams()
  const slug = params.slug as string
  const post = blogPosts[slug]

  if (!post) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Post Not Found
          </h1>
          <Link href="/#blog" className="text-primary-600 hover:underline">
            Back to Blog
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <article className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Link
            href="/#blog"
            className="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:underline mb-8"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Blog
          </Link>

          <header className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <span className="skill-badge">{post.category}</span>
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
              {post.title}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-4">
              {post.excerpt}
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {formatDate(post.date)}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {post.readTime}
              </span>
            </div>
          </header>

          <div className="prose prose-lg dark:prose-invert max-w-none">
            {post.content.split('\n').map((paragraph, index) => {
              if (paragraph.startsWith('# ')) {
                return (
                  <h1 key={index} className="text-3xl font-bold mt-8 mb-4">
                    {paragraph.replace('# ', '')}
                  </h1>
                )
              }
              if (paragraph.startsWith('## ')) {
                return (
                  <h2 key={index} className="text-2xl font-bold mt-8 mb-4">
                    {paragraph.replace('## ', '')}
                  </h2>
                )
              }
              if (paragraph.startsWith('### ')) {
                return (
                  <h3 key={index} className="text-xl font-bold mt-6 mb-3">
                    {paragraph.replace('### ', '')}
                  </h3>
                )
              }
              if (paragraph.startsWith('- ')) {
                return (
                  <li key={index} className="ml-4">
                    {paragraph.replace('- ', '')}
                  </li>
                )
              }
              if (paragraph.match(/^\d+\. /)) {
                return (
                  <li key={index} className="ml-4">
                    {paragraph.replace(/^\d+\. /, '')}
                  </li>
                )
              }
              if (paragraph.startsWith('```')) {
                return null
              }
              if (paragraph.trim() === '') {
                return <br key={index} />
              }
              return (
                <p key={index} className="mb-4 text-gray-700 dark:text-gray-300">
                  {paragraph}
                </p>
              )
            })}
          </div>
        </motion.div>
      </article>
    </div>
  )
}
