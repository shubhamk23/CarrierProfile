# Logging System Integration Guide

## Overview
This guide explains how to integrate and use the comprehensive logging system implemented for both backend (FastAPI) and frontend (Next.js).

## Backend Integration (FastAPI)

### 1. Add Middleware to FastAPI Application

Edit `backend/app/main.py`:

```python
from fastapi import FastAPI
from app.middleware.logging_middleware import (
    LoggingMiddleware,
    PerformanceLoggingMiddleware,
    RequestBodyLoggingMiddleware
)
from app.utils.logger import logger
from app.routers import logs

# Create FastAPI app
app = FastAPI(title="Career Profile API")

# Add logging middleware (order matters!)
app.add_middleware(LoggingMiddleware)
app.add_middleware(PerformanceLoggingMiddleware, slow_request_threshold=1.0)

# Optional: Log request/response bodies (use with caution in production)
# app.add_middleware(RequestBodyLoggingMiddleware, log_request_body=True)

# Include logs router
app.include_router(logs.router, prefix="/api")

# Application startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", version="1.0.0")

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
```

### 2. Using Logger in Route Handlers

```python
from fastapi import APIRouter
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: str):
    logger.info(f"Fetching user", user_id=user_id)

    try:
        # Your business logic here
        user = await fetch_user(user_id)

        logger.info(f"User fetched successfully", user_id=user_id)
        return user

    except Exception as e:
        logger.error(f"Failed to fetch user", user_id=user_id, exc_info=True)
        raise
```

### 3. Session and Request Tracking

The middleware automatically sets session and request IDs. You can access them:

```python
from app.utils.logger import get_session_id, get_request_id, logger

@router.post("/action")
async def perform_action():
    session_id = get_session_id()
    request_id = get_request_id()

    logger.info(
        "Performing action",
        session_id=session_id,
        request_id=request_id
    )
```

### 4. Environment Variables

Add to `backend/.env`:

```bash
# Logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Frontend Integration (Next.js)

### 1. Wrap Application with Error Boundary

Edit `frontend/app/layout.tsx`:

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';
import logger from '@/utils/logger';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}
```

### 2. Using Logger in Components

```tsx
'use client';

import { useEffect } from 'react';
import logger from '@/utils/logger';
import { useComponentLogger, usePageView } from '@/hooks/useLogger';

export default function MyComponent() {
  // Log component lifecycle
  useComponentLogger('MyComponent');

  // Log page view
  usePageView('My Page');

  const handleClick = () => {
    // Log user action
    logger.logUserAction('button_clicked', { button: 'submit' });

    // Your logic here
  };

  return (
    <button onClick={handleClick}>
      Click Me
    </button>
  );
}
```

### 3. Using API Client with Automatic Logging

```tsx
'use client';

import { useState } from 'react';
import apiClient from '@/utils/api-client';

export default function UserProfile() {
  const [user, setUser] = useState(null);

  const fetchUser = async () => {
    try {
      // API call is automatically logged
      const response = await apiClient.get('/users/123');
      setUser(response.data);
    } catch (error) {
      // Error is automatically logged
      console.error('Failed to fetch user:', error);
    }
  };

  return (
    <button onClick={fetchUser}>Load User</button>
  );
}
```

### 4. Performance Tracking

```tsx
import { usePerformanceLogger } from '@/hooks/useLogger';

export default function DataProcessing() {
  const { trackPerformance } = usePerformanceLogger();

  const processData = () => {
    trackPerformance('data_processing', () => {
      // Your expensive operation here
      const result = heavyComputation();
      return result;
    });
  };

  return <button onClick={processData}>Process</button>;
}
```

### 5. Manual Error Logging

```tsx
import logger from '@/utils/logger';

function MyComponent() {
  const handleSubmit = async (data) => {
    try {
      await submitForm(data);
    } catch (error) {
      // Log error with context
      logger.error(
        'Form submission failed',
        'FormSubmit',
        error as Error
      );

      // Show user-friendly message
      alert('Submission failed. Please try again.');
    }
  };
}
```

### 6. Environment Variables

Add to `frontend/.env.local`:

```bash
# API endpoint for backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Logging endpoint (optional, defaults to /api/logs)
NEXT_PUBLIC_LOG_ENDPOINT=/api/logs
```

---

## Log Formats

### Backend JSON Log Format

```json
{
  "timestamp": "2026-02-15T10:30:45.123456Z",
  "level": "INFO",
  "logger": "carrier_profile",
  "message": "Request completed: GET /api/users",
  "module": "logging_middleware",
  "function": "dispatch",
  "line": 85,
  "session_id": "abc123...",
  "request_id": "xyz789...",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_seconds": 0.0234
}
```

### Frontend Console Log Format

```
10:30:45 INFO [PageView][ses:abc123][req:xyz789] Page view: /dashboard
```

---

## Log Levels

### Backend (Python)
- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (deprecated features, etc.)
- **ERROR**: Error messages (handled exceptions)
- **CRITICAL**: Critical errors (system failures)

### Frontend (TypeScript)
- **DEBUG**: Development/debugging information
- **INFO**: Normal application flow
- **WARN**: Warning conditions
- **ERROR**: Error conditions
- **CRITICAL**: Critical failures

---

## Log Files

Backend logs are stored in:
- `backend/logs/app.log` - Human-readable text format
- `backend/logs/app.json.log` - Machine-readable JSON format

---

## Session Tracking

### How It Works

1. **Backend**:
   - Middleware generates/retrieves session ID from cookie
   - Stores in context variable (ContextVar)
   - All logs within request include session ID

2. **Frontend**:
   - Logger generates session ID on first use
   - Stores in sessionStorage
   - All logs include session ID
   - API calls send session ID in headers

3. **End-to-End Tracking**:
   - Frontend sends `X-Session-ID` header
   - Backend correlates with same session
   - Both backend and frontend logs can be linked

---

## Best Practices

### 1. **Choose Appropriate Log Levels**
```python
# ❌ Don't
logger.info("x = 5")  # Too verbose for INFO

# ✅ Do
logger.debug("x = 5")  # Use DEBUG for variable values
logger.info("User registration completed", user_id=user_id)
```

### 2. **Include Relevant Context**
```python
# ❌ Don't
logger.error("Failed")

# ✅ Do
logger.error("User registration failed",
    email=email,
    error_code="DUPLICATE_EMAIL",
    exc_info=True
)
```

### 3. **Use Structured Logging**
```python
# ❌ Don't
logger.info(f"User {user_id} updated profile with {data}")

# ✅ Do
logger.info("User profile updated",
    user_id=user_id,
    fields_updated=list(data.keys())
)
```

### 4. **Don't Log Sensitive Data**
```python
# ❌ Never log
logger.info("User login", password=password)  # NEVER!
logger.info("Payment", credit_card=card_number)  # NEVER!

# ✅ Do
logger.info("User login", email=email)
logger.info("Payment processed", last_4_digits=card[-4:])
```

### 5. **Frontend: Batch Logs for Performance**
The frontend logger automatically batches logs when remote logging is enabled to reduce network overhead.

---

## Monitoring & Analysis

### Viewing Logs

#### Development
- **Backend**: Console output with colors
- **Frontend**: Browser console

#### Production
- **Backend**: Check `logs/app.json.log` for structured data
- **Frontend**: Logs sent to `/api/logs` endpoint

### Searching Logs

```bash
# Search for errors in a specific session
jq 'select(.level == "ERROR" and .session_id == "abc123")' backend/logs/app.json.log

# Find slow requests
jq 'select(.duration_seconds > 1)' backend/logs/app.json.log

# Count errors by type
jq -r 'select(.level == "ERROR") | .exception.type' backend/logs/app.json.log | sort | uniq -c
```

---

## Troubleshooting

### Backend Logs Not Appearing

1. Check LOG_LEVEL in .env
2. Ensure logs directory exists and is writable
3. Verify middleware is added to FastAPI app

### Frontend Logs Not Sent to Backend

1. Check NEXT_PUBLIC_LOG_ENDPOINT is correct
2. Verify /api/logs endpoint is accessible
3. Check browser console for fetch errors

### Session IDs Not Correlating

1. Ensure frontend sends X-Session-ID header
2. Verify CORS allows custom headers
3. Check middleware processes headers correctly

---

## Performance Considerations

### Backend
- JSON logging has minimal overhead (~1-2% for typical apps)
- Log files rotate automatically (implement logrotate)
- Use DEBUG level sparingly in production

### Frontend
- Logs batched to reduce API calls
- Session ID stored in sessionStorage (cleared on tab close)
- Remote logging disabled in development by default

---

## Future Enhancements

1. **Log Aggregation**: Send logs to ELK, Datadog, or CloudWatch
2. **Real-time Monitoring**: WebSocket for live log streaming
3. **Alert System**: Automatic alerts on error thresholds
4. **Analytics Dashboard**: Visualize logs and metrics
5. **Log Retention**: Automatic cleanup of old logs

---

*Last Updated: 2026-02-15*
