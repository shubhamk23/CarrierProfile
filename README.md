# CarrierProfile - ML Engineer Portfolio Website

A modern, production-ready career portfolio website built with Next.js 14 and FastAPI, featuring real-time contact form, database storage, and comprehensive SEO optimization.

## Live Demo

- **Frontend:** [Coming Soon - Deploy to Vercel]
- **API:** [Coming Soon - Deploy to Vercel]
- **API Documentation:** [Your API URL]/docs

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router) with TypeScript
- **Styling:** Tailwind CSS + Framer Motion (animations)
- **Theme:** Dark/Light mode with next-themes
- **Icons:** Lucide React
- **Form Validation:** React Hook Form + Zod
- **Deployment:** Vercel with Edge Network CDN

### Backend
- **Framework:** FastAPI (Python 3.9+)
- **Database:** PostgreSQL (via Supabase)
- **ORM:** SQLAlchemy with async support (asyncpg)
- **Migrations:** Alembic
- **Email:** Resend API
- **Rate Limiting:** SlowAPI (5 requests/hour per IP)
- **Deployment:** Vercel Serverless Functions

### Infrastructure
- **Database:** Supabase (PostgreSQL + Storage)
- **Email Service:** Resend
- **Hosting:** Vercel (Frontend + Backend)
- **CI/CD:** GitHub Actions
- **Storage:** Supabase Storage (resume, assets)

## Features

- ✅ Responsive design (mobile-first)
- ✅ Dark/Light mode toggle
- ✅ Smooth scroll navigation
- ✅ Animated sections with Framer Motion
- ✅ Interactive experience timeline
- ✅ Skills grid with categories
- ✅ Project showcase
- ✅ Contact form with database storage
- ✅ Email notifications via Resend
- ✅ Rate limiting (5 submissions/hour)
- ✅ Blog section with dynamic routing
- ✅ SEO optimized (sitemap, robots.txt, meta tags)
- ✅ Security headers (CSP, HSTS, etc.)
- ✅ Alembic database migrations
- ✅ GitHub Actions CI/CD
- ✅ Automatic preview deployments

## Project Structure

```
CarrierProfile/
├── .github/
│   └── workflows/
│       ├── backend-ci.yml        # Backend linting & tests
│       └── frontend-ci.yml       # Frontend linting & build
│
├── frontend/                     # Next.js application
│   ├── app/
│   │   ├── layout.tsx            # Root layout with metadata
│   │   ├── page.tsx              # Home page
│   │   ├── globals.css
│   │   ├── sitemap.ts            # Dynamic sitemap
│   │   ├── robots.ts             # Robots.txt
│   │   └── blog/[slug]/page.tsx  # Blog post pages
│   ├── components/
│   │   ├── Hero.tsx
│   │   ├── About.tsx
│   │   ├── Experience.tsx
│   │   ├── Skills.tsx
│   │   ├── Projects.tsx
│   │   ├── Education.tsx
│   │   ├── Blog.tsx
│   │   ├── Contact.tsx           # Contact form with validation
│   │   ├── Navigation.tsx
│   │   └── ThemeToggle.tsx
│   ├── lib/
│   │   └── api.ts                # API client
│   ├── next.config.js            # Security headers, CSP
│   ├── vercel.json               # Additional security headers
│   └── package.json
│
├── backend/                      # FastAPI application
│   ├── alembic/                  # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── app/
│   │   ├── main.py               # FastAPI app with CORS
│   │   ├── config.py             # Settings (Pydantic)
│   │   ├── models.py             # Pydantic models
│   │   ├── database/
│   │   │   ├── connection.py    # Async SQLAlchemy setup
│   │   │   └── models.py        # Database models
│   │   ├── middleware/
│   │   │   └── rate_limit.py    # Rate limiting
│   │   ├── routers/
│   │   │   ├── profile.py
│   │   │   ├── blog.py
│   │   │   └── contact.py       # Contact form + Resend
│   │   └── data/
│   │       └── profile.json
│   ├── requirements.txt
│   ├── alembic.ini
│   └── vercel.json
│
├── .gitignore
├── README.md
└── prd.md
```

## Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL (local) or Supabase account
- Git

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/CarrierProfile.git
cd CarrierProfile
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
```

Edit `backend/.env` with your configuration:

```env
# Database (Required)
DATABASE_URL=postgresql://user:password@localhost:5432/carrierprofile

# Security (Required)
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# Email (Optional for local dev)
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=onboarding@resend.dev
RESEND_TO_EMAIL=your-email@example.com

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]

# Application
DEBUG=True
RATE_LIMIT_ENABLED=True
RATE_LIMIT_TIMES=5
RATE_LIMIT_SECONDS=3600
```

Run database migrations:

```bash
# Initialize database schema
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NEXT_PUBLIC_RESUME_URL=/resume.pdf
```

Start the frontend:

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### 4. Verify Setup

- Visit http://localhost:3000 - Frontend should load
- Visit http://localhost:8000/docs - API documentation
- Submit contact form - Check console for logs
- Check database for stored message

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | Application secret key | Yes | - | Generate with `openssl rand -hex 32` |
| `RESEND_API_KEY` | Resend email API key | No* | "" | `re_123...` |
| `RESEND_FROM_EMAIL` | Email sender address | No | `onboarding@resend.dev` | `noreply@yourdomain.com` |
| `RESEND_TO_EMAIL` | Email recipient address | No* | "" | `you@example.com` |
| `ALLOWED_ORIGINS` | CORS allowed origins (JSON array) | Yes | `["http://localhost:3000"]` | `["https://yoursite.com"]` |
| `DEBUG` | Debug mode | No | `False` | `True` or `False` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | No | `True` | `True` or `False` |
| `RATE_LIMIT_TIMES` | Max requests per period | No | `5` | `5` |
| `RATE_LIMIT_SECONDS` | Rate limit period (seconds) | No | `3600` | `3600` |

*Required for production email notifications

### Frontend Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | - | `https://your-api.vercel.app` |
| `NEXT_PUBLIC_BASE_URL` | Frontend base URL | Yes | - | `https://yoursite.vercel.app` |
| `NEXT_PUBLIC_RESUME_URL` | Resume PDF URL | No | `/resume.pdf` | Supabase Storage URL |

## API Endpoints

| Method | Endpoint | Description | Rate Limited |
|--------|----------|-------------|--------------|
| GET | `/` | API info | No |
| GET | `/api/health` | Health check | No |
| GET | `/api/profile` | Full profile data | No |
| GET | `/api/experience` | Work experience list | No |
| GET | `/api/skills` | Skills by category | No |
| GET | `/api/projects` | Project details | No |
| GET | `/api/achievements` | Awards & certifications | No |
| GET | `/api/blog` | Blog posts list | No |
| GET | `/api/blog/{slug}` | Single blog post | No |
| POST | `/api/contact` | Submit contact form | Yes (5/hour) |
| GET | `/api/contact/messages` | Get all messages (admin) | No |

## Deployment Guide

### Prerequisites

1. **GitHub Account** - For repository hosting and CI/CD
2. **Vercel Account** - For hosting (free tier)
3. **Supabase Account** - For database and storage (free tier)
4. **Resend Account** - For email notifications (free tier)

### Step 1: Supabase Setup

1. Go to https://supabase.com/dashboard
2. Create new project: `carrier-profile-prod`
3. Choose region closest to your users
4. Copy database connection string from Settings > Database > Connection String > URI
5. Create storage bucket for resume:
   - Storage > Create bucket
   - Name: `public-assets`, Public: Yes
   - Upload your resume PDF
   - Copy public URL

### Step 2: Resend Setup

1. Sign up at https://resend.com
2. Dashboard > API Keys > Create API Key
3. Copy the API key (starts with `re_`)
4. Use `onboarding@resend.dev` for free tier

### Step 3: Push to GitHub

```bash
# Add GitHub remote (create repo first on GitHub)
git remote add origin https://github.com/YOUR_USERNAME/CarrierProfile.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy Backend to Vercel

```bash
cd backend
npm install -g vercel  # If not installed
vercel login
vercel --prod
```

Configure environment variables in Vercel Dashboard:
- Go to https://vercel.com/YOUR_USERNAME/PROJECT/settings/environment-variables
- Add all backend environment variables (see table above)
- Redeploy: `vercel --prod`

Copy the production URL (e.g., `https://carrier-profile-api.vercel.app`)

### Step 5: Run Database Migrations

```bash
cd backend
# Set DATABASE_URL in .env to production Supabase URL
alembic upgrade head
```

Verify tables created in Supabase > Table Editor

### Step 6: Deploy Frontend to Vercel

```bash
cd frontend
vercel --prod
```

Configure environment variables in Vercel Dashboard:
- `NEXT_PUBLIC_API_URL` = Backend URL from Step 4
- `NEXT_PUBLIC_BASE_URL` = Frontend Vercel URL
- `NEXT_PUBLIC_RESUME_URL` = Supabase resume URL from Step 1

Redeploy: `vercel --prod`

### Step 7: Update Backend CORS

Update backend `ALLOWED_ORIGINS` in Vercel to include frontend URL:
```
["http://localhost:3000","https://your-frontend.vercel.app"]
```

Redeploy backend: `cd backend && vercel --prod`

### Step 8: Connect GitHub for Auto-Deploy

In Vercel Dashboard for both projects:
1. Settings > Git > Connect Git Repository
2. Select CarrierProfile repo
3. Backend: Root Directory = `backend`
4. Frontend: Root Directory = `frontend`
5. Production Branch = `main`

Now every push to `main` triggers automatic deployment!

## Database Migrations

### Create New Migration

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Local
alembic upgrade head

# Production (set DATABASE_URL to production)
DATABASE_URL=postgresql://... alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1  # Rollback one migration
```

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run build  # Test production build
```

### API Testing

```bash
# Health check
curl https://your-api.vercel.app/api/health

# Contact form
curl -X POST https://your-api.vercel.app/api/contact \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","subject":"Test","message":"Testing"}'
```

## CI/CD Pipeline

GitHub Actions workflows automatically run on push/PR:

### Backend CI (`backend-ci.yml`)
- Runs on changes to `backend/**`
- Python setup (3.9)
- Install dependencies
- Flake8 linting
- Black code formatting check
- Pytest (if tests exist)

### Frontend CI (`frontend-ci.yml`)
- Runs on changes to `frontend/**`
- Node.js setup (18)
- Install dependencies
- ESLint
- Production build verification

## Security

### Implemented Security Measures

- ✅ HTTPS enforced (Vercel automatic)
- ✅ Security headers (CSP, HSTS, X-Frame-Options, etc.)
- ✅ CORS configured (no wildcards in production)
- ✅ Rate limiting on contact form (5/hour)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (React escaping + CSP)
- ✅ Environment variables for secrets
- ✅ No secrets in repository
- ✅ Input validation (Pydantic + Zod)

### Security Headers

Test your deployment: https://securityheaders.com

Expected headers:
- `Content-Security-Policy`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy`

## Performance

### Optimization Features

- Next.js Image optimization
- Static generation where possible
- Vercel Edge Network CDN
- Database connection pooling
- Framer Motion lazy loading
- Code splitting (automatic)

### Target Metrics (Lighthouse)

- Performance: >90
- Accessibility: >90
- Best Practices: >90
- SEO: >90

Test: https://pagespeed.web.dev

## SEO

### Implemented SEO Features

- ✅ Dynamic sitemap (`/sitemap.xml`)
- ✅ Robots.txt (`/robots.txt`)
- ✅ Meta tags (title, description, keywords)
- ✅ Open Graph tags
- ✅ Semantic HTML
- ✅ Mobile responsive
- ✅ Fast loading (<2s)

### Verify SEO

- Sitemap: `https://yoursite.com/sitemap.xml`
- Robots: `https://yoursite.com/robots.txt`
- Google Search Console: Submit sitemap

## Troubleshooting

### Backend Issues

**Database connection fails:**
```bash
# Check DATABASE_URL format
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT version();"
```

**Migrations fail:**
```bash
# Check current revision
alembic current

# Reset to head
alembic upgrade head
```

### Frontend Issues

**Build fails:**
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

**API requests fail:**
- Check `NEXT_PUBLIC_API_URL` is set correctly
- Verify backend CORS includes frontend URL
- Check browser console for errors

## Customization

### Update Profile Data

Edit `backend/app/data/profile.json` with your information

### Modify Colors

Edit `frontend/tailwind.config.ts`:
```typescript
colors: {
  primary: {
    50: '#...',
    // ... your color palette
  }
}
```

### Add Blog Posts

Edit `backend/app/routers/blog.py` to add new blog posts

### Change Resume

Replace `frontend/public/resume.pdf` or upload to Supabase Storage

## Monitoring (Future Enhancement)

Recommended tools for production monitoring:
- **Error Tracking:** Sentry
- **Uptime Monitoring:** UptimeRobot or BetterStack
- **Analytics:** Vercel Analytics, Google Analytics
- **Performance:** Vercel Speed Insights

## Contributing

This is a personal portfolio project, but feel free to fork and adapt for your own use!

## License

MIT

## Author

**Shubham Khanapure**
Senior ML Engineer | Generative AI & Computer Vision Specialist

- Email: shubhamkhanapure@gmail.com
- LinkedIn: [linkedin.com/in/shubham-khanapure-4191b1127](https://www.linkedin.com/in/shubham-khanapure-4191b1127/)
- GitHub: [github.com/shubhamk23](https://github.com/shubhamk23)

---

Built with ❤️ using Next.js, FastAPI, and modern web technologies.
