# Deployment Implementation Checklist

## Do this first: rotate the leaked database credential

A real Supabase password was committed to `backend/.env.example` and pushed to
a **public** repository. The file has been scrubbed, but the credential is
still in git history, so scrubbing alone does not make it safe.

- [ ] Supabase Dashboard > Settings > Database > **Reset database password**
- [ ] Update `DATABASE_URL` in Vercel project env vars with the new password
      (use the pooler endpoint, port 6543)
- [ ] Redeploy the backend so it picks up the new value
- [ ] Confirm `GET /api/health` still returns `{"status": "healthy"}` and one
      real contact form submission lands in the database

History was deliberately **not** rewritten - a force-push over a public repo
with an already-merged PR carries more risk than it removes. Rotation is what
makes the old value worthless.

The unauthenticated `GET /api/contact/messages` endpoint, which exposed every
visitor's name, email, IP address, and message, has been deleted. Read
submissions in the Supabase dashboard or via the Resend notification email.


## ✅ Completed Implementation Tasks

All code changes and configurations have been implemented according to the deployment plan. Here's what was completed:

### Phase 1: Pre-Deployment Setup
- ✅ Root `.gitignore` created with comprehensive exclusions
- ✅ Git repository initialized
- ✅ Initial commit created
- ✅ Alembic migrations initialized and configured
- ✅ `alembic.ini` configured to use app settings
- ✅ `alembic/env.py` configured with database models

### Phase 2: Backend Updates
- ✅ `resend==0.8.0` added to `requirements.txt`
- ✅ `psycopg2-binary==2.9.9` added for Alembic migrations
- ✅ `config.py` updated with Resend settings (resend_api_key, resend_from_email, resend_to_email)
- ✅ `main.py` CORS updated to use `settings.allowed_origins` (no wildcards)
- ✅ `contact.py` router completely rewritten with:
  - Database storage using SQLAlchemy async
  - Resend email integration with HTML templates
  - Fallback to JSON file storage
  - Rate limiting integration
  - Error handling and logging

### Phase 3: Frontend Updates
- ✅ `Hero.tsx` updated to use `process.env.NEXT_PUBLIC_RESUME_URL`
- ✅ `next.config.js` updated with:
  - Security headers (CSP, HSTS, etc.)
  - Image domains for Supabase
  - Remote patterns for Supabase CDN
- ✅ `sitemap.ts` created with dynamic sitemap generation
- ✅ `robots.ts` created with proper crawling rules
- ✅ `layout.tsx` updated with `metadataBase`
- ✅ `vercel.json` created with security headers

### Phase 4: CI/CD Setup
- ✅ `.github/workflows/backend-ci.yml` created with:
  - Python 3.9 setup
  - Dependency caching
  - Flake8 linting
  - Black formatting check
  - Pytest support
- ✅ `.github/workflows/frontend-ci.yml` created with:
  - Node.js 18 setup
  - NPM dependency caching
  - ESLint checks
  - Production build verification

### Phase 5: Documentation
- ✅ `README.md` completely updated with:
  - Tech stack documentation
  - Local development setup
  - Environment variables reference tables
  - API endpoints documentation
  - Step-by-step deployment guide
  - Database migrations guide
  - Security and performance sections
  - Troubleshooting guide
  - SEO optimization details

## 📝 Files Modified/Created

### New Files:
- `.gitignore`
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/README`
- `frontend/app/sitemap.ts`
- `frontend/app/robots.ts`
- `frontend/vercel.json`
- `DEPLOYMENT_CHECKLIST.md` (this file)

### Modified Files:
- `backend/requirements.txt` (added resend, psycopg2-binary)
- `backend/app/config.py` (added Resend settings)
- `backend/app/main.py` (fixed CORS)
- `backend/app/routers/contact.py` (complete rewrite)
- `frontend/components/Hero.tsx` (dynamic resume URL)
- `frontend/next.config.js` (security headers, images)
- `frontend/app/layout.tsx` (metadataBase)
- `README.md` (comprehensive update)

## 🚀 Next Steps: Deployment to Production

You're now ready to deploy! Follow these steps in order:

### Step 1: Install Backend Dependencies (5 minutes)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

This installs:
- `resend==0.8.0` for email
- `psycopg2-binary==2.9.9` for migrations

### Step 2: Supabase Setup (10-15 minutes)

1. Go to https://supabase.com/dashboard
2. Create new project: `carrier-profile-prod`
3. Choose region closest to your users
4. Save the database password
5. Copy DATABASE_URL from: Settings > Database > Connection String > URI
   - Format: `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres`

6. Create storage bucket:
   - Storage > Create bucket
   - Name: `public-assets`
   - Public: Yes
   - Upload `frontend/public/resume.pdf`
   - Copy the public URL

### Step 3: Resend Setup (5 minutes)

1. Sign up at https://resend.com
2. Dashboard > API Keys > Create API Key
3. Name: `CarrierProfile Production`
4. Copy API key (starts with `re_`)
5. Use `onboarding@resend.dev` as sender (free tier)

### Step 4: Create GitHub Repository (5 minutes)

1. Go to https://github.com/new
2. Repository name: `CarrierProfile`
3. Visibility: Public or Private (your choice)
4. Don't initialize with README (we already have one)
5. Create repository
6. Copy the repository URL

### Step 5: Push to GitHub (2 minutes)

```bash
cd /Users/shubhamkhanapure/Developer/Personal\ Project\ Latest/CarrierProfile
git remote add origin https://github.com/YOUR_USERNAME/CarrierProfile.git
git push -u origin main
```

### Step 6: Deploy Backend to Vercel (10 minutes)

```bash
cd backend
npm install -g vercel  # If not already installed
vercel login
vercel --prod
```

Follow prompts:
- Project name: `carrier-profile-api` (or your choice)
- Root directory: `./`

After deployment:
1. Go to Vercel Dashboard > Your Project > Settings > Environment Variables
2. Add these variables:
   - `DATABASE_URL` = [Supabase URL from Step 2 - use the **pooler** endpoint,
     port 6543, not the direct 5432 connection; serverless functions fan out
     and PgBouncer is what absorbs that]
   - `RESEND_API_KEY` = [From Step 3]
   - `RESEND_FROM_EMAIL` = `onboarding@resend.dev`
   - `RESEND_TO_EMAIL` = [Your email]
   - `ALLOWED_ORIGINS` = `["http://localhost:3000"]` (will update after frontend)
   - `DEBUG` = `False`
   - `RATE_LIMIT_ENABLED` = `True`

3. Redeploy: `vercel --prod`
4. Copy production URL (e.g., `https://carrier-profile-api.vercel.app`)

### Step 7: Run Database Migrations (5 minutes)

```bash
cd backend
source venv/bin/activate

# Create .env with production DATABASE_URL
echo "DATABASE_URL=your-supabase-url-here" > .env
```

**If this database is brand new** (no `contact_messages` table yet):

```bash
alembic upgrade head
```

**If `contact_messages` already exists** (created by the old
`create_all`-at-startup behaviour), tell Alembic its history starts at the
baseline first, or `upgrade` will try to `CREATE TABLE` over the live table:

```bash
alembic stamp 0001_baseline   # records the baseline, runs no DDL
alembic upgrade head          # applies only 0002's cleanup
```

Migration `0002` drops the redundant `timestamp`, `read`, and `updated_at`
columns and four unused indexes. **Take a Supabase backup first if you have
submissions you care about** - `timestamp` duplicates `created_at`, so no
unique data is lost, but the drop is not reversible without the backup.

Verify in Supabase:
- Table Editor should show `contact_messages` and `alembic_version`
- `contact_messages` should have exactly: `id`, `name`, `email`, `subject`,
  `message`, `ip_address`, `user_agent`, `created_at`

### Step 8: Deploy Frontend to Vercel (10 minutes)

```bash
cd frontend
vercel --prod
```

Follow prompts:
- Project name: `carrier-profile` (or your choice)
- Root directory: `./`

After deployment:
1. Go to Vercel Dashboard > Your Project > Settings > Environment Variables
2. Add these variables:
   - `NEXT_PUBLIC_API_URL` = [Backend URL from Step 6]
   - `NEXT_PUBLIC_BASE_URL` = [Frontend Vercel URL you just got]
   - `NEXT_PUBLIC_RESUME_URL` = [Supabase Storage URL from Step 2]

3. Redeploy: `vercel --prod`
4. Copy production URL (e.g., `https://carrier-profile.vercel.app`)

### Step 9: Update Backend CORS (5 minutes)

1. Go to backend project in Vercel Dashboard
2. Settings > Environment Variables
3. Edit `ALLOWED_ORIGINS`:
   ```
   ["http://localhost:3000","https://your-frontend.vercel.app"]
   ```
4. Redeploy backend: `cd backend && vercel --prod`

### Step 10: Connect GitHub for Auto-Deploy (10 minutes)

**Backend:**
1. Vercel Dashboard > carrier-profile-api > Settings > Git
2. Connect Git Repository
3. Select `CarrierProfile` repo
4. Root Directory: `backend`
5. Production Branch: `main`
6. Enable automatic deployments

**Frontend:**
1. Vercel Dashboard > carrier-profile > Settings > Git
2. Connect Git Repository
3. Select `CarrierProfile` repo
4. Root Directory: `frontend`
5. Production Branch: `main`
6. Enable automatic deployments

### Step 11: Test Production Deployment (10 minutes)

**API Health Check:**
```bash
curl https://your-api.vercel.app/api/health
```

**Frontend:**
1. Visit your frontend URL
2. Test all sections scroll correctly
3. Test dark/light mode toggle
4. Test contact form:
   - Fill out form
   - Submit
   - Check Supabase for entry
   - Check your email for notification
5. Test resume download
6. Check browser console for errors (should be none)

**SEO:**
- Visit `/sitemap.xml` - Should list all sections
- Visit `/robots.txt` - Should show crawling rules

**Security Headers:**
- Visit https://securityheaders.com
- Enter your site URL
- Should get grade A or B

### Step 12: Update README (2 minutes)

Update live demo links in README.md:

```markdown
## Live Demo

- **Frontend:** https://your-frontend.vercel.app
- **API:** https://your-api.vercel.app
- **API Documentation:** https://your-api.vercel.app/docs
```

Commit and push:
```bash
git add README.md
git commit -m "Add production URLs to README"
git push origin main
```

## 🎯 Post-Deployment Checklist

After deployment, verify:

- [ ] Frontend loads at production URL
- [ ] API responds at /api/health
- [ ] API docs accessible at /docs
- [ ] Contact form saves to Supabase
- [ ] Email notifications work via Resend
- [ ] Rate limiting active (try 6 submissions)
- [ ] Resume downloads from Supabase
- [ ] `/sitemap.xml` accessible
- [ ] `/robots.txt` accessible
- [ ] Security headers present
- [ ] No console errors
- [ ] Mobile responsive
- [ ] GitHub Actions workflows passing
- [ ] Auto-deploy works (test with small change)

## 🔧 Useful Commands

### Local Development

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Vercel Deployment

```bash
# Deploy backend
cd backend && vercel --prod

# Deploy frontend
cd frontend && vercel --prod

# View logs
vercel logs
```

### Git Operations

```bash
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Description"

# Push (triggers auto-deploy)
git push origin main
```

## 📊 Estimated Timeline

- **Step 1 (Dependencies):** 5 minutes
- **Step 2 (Supabase):** 15 minutes
- **Step 3 (Resend):** 5 minutes
- **Step 4 (GitHub):** 5 minutes
- **Step 5 (Push):** 2 minutes
- **Step 6 (Backend Deploy):** 10 minutes
- **Step 7 (Migrations):** 5 minutes
- **Step 8 (Frontend Deploy):** 10 minutes
- **Step 9 (CORS Update):** 5 minutes
- **Step 10 (Auto-Deploy):** 10 minutes
- **Step 11 (Testing):** 10 minutes
- **Step 12 (Update README):** 2 minutes

**Total: ~90 minutes (1.5 hours)**

## 🆘 Troubleshooting

### Backend deployment fails
- Check all environment variables are set in Vercel
- Verify DATABASE_URL format is correct
- Check Vercel logs: `vercel logs`

### Frontend deployment fails
- Verify NEXT_PUBLIC_API_URL is set
- Check build logs in Vercel Dashboard
- Try local build: `npm run build`

### Contact form doesn't work
- Check browser console for errors
- Verify API URL is correct
- Check backend CORS includes frontend URL
- Verify Supabase tables exist

### Email not received
- Check RESEND_API_KEY is set
- Verify RESEND_TO_EMAIL is your email
- Check Resend dashboard for logs
- Check spam folder

### Database connection fails
- Verify DATABASE_URL is correct
- Check Supabase project is running
- Test connection: `psql $DATABASE_URL -c "SELECT 1;"`

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ Production URLs are accessible
2. ✅ All features work end-to-end
3. ✅ Contact form saves and sends email
4. ✅ No errors in production
5. ✅ Security headers configured
6. ✅ SEO files accessible
7. ✅ Auto-deployment active
8. ✅ Mobile responsive verified

## 📚 Additional Resources

- **Deployment Plan:** See full deployment plan in the initial request
- **README.md:** Comprehensive local dev and deployment guide
- **prd.md:** Product requirements document
- **Vercel Docs:** https://vercel.com/docs
- **Supabase Docs:** https://supabase.com/docs
- **Alembic Docs:** https://alembic.sqlalchemy.org
- **Resend Docs:** https://resend.com/docs

## 🔄 Continuous Integration

Your project now has GitHub Actions configured:

- **Backend CI:** Runs linting and tests on backend changes
- **Frontend CI:** Runs linting and build on frontend changes
- **Auto-Deploy:** Vercel deploys on every push to main

To see workflow runs:
- Go to GitHub repo > Actions tab

## 🚀 You're Ready to Deploy!

All code is ready. Follow Steps 1-12 above to deploy to production.

Good luck! 🎉
