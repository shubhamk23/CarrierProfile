# CarrierProfile - Working Memory

## Project Overview
Full-stack career profile application with FastAPI backend and Next.js frontend.

## Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn with async support
- **Database**: PostgreSQL with SQLAlchemy 2.0.25 (async)
- **Migrations**: Alembic 1.13.1
- **Validation**: Pydantic 2.5.3
- **Rate Limiting**: SlowAPI 0.1.9
- **Email Service**: Resend 0.8.0

### Frontend
- **Framework**: Next.js 14.2.0
- **Runtime**: React 18.2.0
- **Language**: TypeScript 5.4.0
- **Styling**: Tailwind CSS 3.4.0
- **Forms**: React Hook Form 7.51.0 + Zod 3.23.0
- **Animations**: Framer Motion 11.0.0
- **Theming**: next-themes 0.3.0
- **Icons**: Lucide React 0.400.0

## Project Structure

```
CarrierProfile/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application entry
│   │   ├── config.py        # Configuration management
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── routers/         # API route handlers
│   │   ├── middleware/      # Custom middleware
│   │   └── database/        # Database connection & utilities
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
│
├── frontend/                # Next.js frontend
│   ├── app/                 # Next.js 14 app directory
│   ├── components/          # React components
│   ├── public/              # Static assets
│   └── package.json         # Node dependencies
│
└── .git/                    # Git repository
```

## Key Features
- Async database operations
- Rate limiting on API endpoints
- Email validation and sending
- Form validation with Zod
- Dark/light theme support
- Responsive design with Tailwind

## Environment Setup
- Backend: Python virtual environment in `backend/venv/`
- Frontend: Node modules in `frontend/node_modules/`
- Database: PostgreSQL (connection via asyncpg)

## Current Focus
- Implementing comprehensive logging mechanism
- Session tracking for end-to-end request monitoring

## Notes
- Backend deployed on Vercel
- Frontend deployed on Vercel
- Using Alembic for database migrations
- Email service configured with Resend

---
*Last updated: 2026-02-15*
