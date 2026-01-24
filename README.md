# Career Profile Website

A modern, single-page career portfolio website built with Next.js and FastAPI.

## Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router) with TypeScript
- **Styling:** Tailwind CSS + Framer Motion (animations)
- **Theme:** Dark/Light mode with next-themes
- **Icons:** Lucide React
- **Form Validation:** React Hook Form + Zod

### Backend
- **Framework:** FastAPI (Python)
- **Data Storage:** JSON files (can be extended to use a database)

## Project Structure

```
CarrierProfile/
├── frontend/                 # Next.js application
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── blog/[slug]/page.tsx
│   ├── components/
│   │   ├── Hero.tsx
│   │   ├── About.tsx
│   │   ├── Experience.tsx
│   │   ├── Skills.tsx
│   │   ├── Projects.tsx
│   │   ├── Achievements.tsx
│   │   ├── Education.tsx
│   │   ├── Blog.tsx
│   │   ├── Contact.tsx
│   │   ├── Navigation.tsx
│   │   ├── ThemeToggle.tsx
│   │   └── Footer.tsx
│   └── lib/
│       └── api.ts
│
├── backend/                  # FastAPI application
│   ├── api/
│   │   └── index.py
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routers/
│   │   │   ├── profile.py
│   │   │   ├── blog.py
│   │   │   └── contact.py
│   │   └── data/
│   │       └── profile.json
│   ├── requirements.txt
│   └── vercel.json
│
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.9+
- npm or yarn

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/profile | Full profile data |
| GET | /api/experience | Work experience list |
| GET | /api/skills | Skills by category |
| GET | /api/projects | Project details |
| GET | /api/achievements | Awards & certifications |
| GET | /api/blog | Blog posts list |
| GET | /api/blog/{slug} | Single blog post |
| POST | /api/contact | Submit contact form |

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import the project in Vercel
3. Configure build settings:
   - Frontend: Root directory = `frontend`, Build command = `npm run build`
   - Backend: Deploy separately or use Vercel Serverless Functions

### Environment Variables

Frontend (`.env.local`):
```
NEXT_PUBLIC_API_URL=https://your-api-url.vercel.app
```

## Features

- Responsive design (mobile-first)
- Dark/Light mode toggle
- Smooth scroll navigation
- Animated sections with Framer Motion
- Interactive experience timeline
- Skills grid with categories
- Project showcase with expandable details
- Contact form with validation
- Blog section with article pages
- SEO optimized

## Customization

1. Update `backend/app/data/profile.json` with your information
2. Modify blog posts in `backend/app/routers/blog.py`
3. Customize colors in `frontend/tailwind.config.ts`
4. Add your resume PDF to `frontend/public/resume.pdf`

## License

MIT
