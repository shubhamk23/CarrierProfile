# Logging System Quick Start

## 🚀 Get Started in 5 Minutes

### Backend (FastAPI) - Quick Setup

#### 1. Import and use the logger

```python
# In any route handler or function
from app.utils.logger import logger

@router.get("/example")
async def example_endpoint():
    logger.info("Processing request")

    try:
        result = perform_operation()
        logger.info("Operation successful", result_count=len(result))
        return result
    except Exception as e:
        logger.error("Operation failed", exc_info=True)
        raise
```

#### 2. Add middleware (in main.py)

```python
from app.middleware.logging_middleware import LoggingMiddleware

app.add_middleware(LoggingMiddleware)
```

That's it! Every request will now be automatically logged with session tracking.

---

### Frontend (Next.js) - Quick Setup

#### 1. Import and use the logger

```tsx
'use client';

import logger from '@/utils/logger';

export default function MyComponent() {
  const handleClick = () => {
    logger.info('Button clicked', 'MyComponent');

    // Your logic here
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

#### 2. Use the API client for automatic logging

```tsx
import apiClient from '@/utils/api-client';

const fetchData = async () => {
  // Automatically logs the API call
  const response = await apiClient.get('/api/data');
  return response.data;
};
```

#### 3. Add Error Boundary (in layout.tsx)

```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}
```

Done! Your app now has comprehensive error tracking and logging.

---

## 📊 What Gets Logged Automatically?

### Backend
✅ All HTTP requests (method, path, status, duration)
✅ Session and request IDs
✅ Client IP and user agent
✅ Slow requests (>1 second)
✅ Errors with full stack traces

### Frontend
✅ Page views
✅ API calls (method, URL, status, duration)
✅ User actions
✅ Unhandled errors and promise rejections
✅ Component lifecycle events (when using hooks)

---

## 🎯 Common Use Cases

### 1. Log a User Action

```tsx
import logger from '@/utils/logger';

const handleFormSubmit = (data) => {
  logger.logUserAction('form_submitted', {
    form_type: 'contact',
    fields: Object.keys(data)
  });
};
```

### 2. Track Performance

```tsx
import { usePerformanceLogger } from '@/hooks/useLogger';

const { trackPerformance } = usePerformanceLogger();

const processData = () => {
  trackPerformance('heavy_calculation', () => {
    // Your expensive operation
  });
};
```

### 3. Log Component Lifecycle

```tsx
import { useComponentLogger } from '@/hooks/useLogger';

function MyComponent() {
  useComponentLogger('MyComponent');
  // Component mount/unmount automatically logged

  return <div>Content</div>;
}
```

### 4. Backend: Log with Extra Context

```python
from app.utils.logger import logger

logger.info(
    "User profile updated",
    user_id=user_id,
    fields_changed=['email', 'name'],
    ip_address=request.client.host
)
```

### 5. Backend: Track Custom Sessions

```python
from app.utils.logger import set_user_id

@router.post("/login")
async def login(credentials):
    user = authenticate(credentials)
    set_user_id(user.id)  # Now all logs include user_id

    logger.info("User logged in", email=user.email)
```

---

## 📁 Where Are Logs Stored?

### Backend
- **Console**: Colored output during development
- **Files**:
  - `backend/logs/app.log` - Human-readable
  - `backend/logs/app.json.log` - Machine-readable (JSON)

### Frontend
- **Console**: Browser developer tools
- **Remote**: Sent to backend `/api/logs` endpoint (in production)

---

## 🔍 Viewing Logs

### Development

**Backend**: Just look at your terminal
**Frontend**: Open browser console (F12)

### Production

**Search JSON logs**:
```bash
# All errors
jq 'select(.level == "ERROR")' backend/logs/app.json.log

# Specific session
jq 'select(.session_id == "abc123")' backend/logs/app.json.log

# Slow requests
jq 'select(.duration_seconds > 1)' backend/logs/app.json.log
```

---

## 🎚️ Log Levels

Use the right level:

- **DEBUG**: Variable values, detailed flow (dev only)
- **INFO**: Normal operations (user logged in, order created)
- **WARN**: Unexpected but handled (deprecated API used)
- **ERROR**: Errors that are caught (failed API call, validation error)
- **CRITICAL**: System failures (database down, out of memory)

---

## ⚡ Performance Tips

### Backend
```python
# ✅ Good - Only logs in DEBUG mode
logger.debug("Processing items", count=len(items))

# ❌ Avoid - Expensive operation always runs
logger.debug(f"Data: {expensive_serialization(data)}")

# ✅ Better
if logger.logger.isEnabledFor(logging.DEBUG):
    logger.debug("Data", data=expensive_serialization(data))
```

### Frontend
```tsx
// ✅ Good - Logs batched automatically
logger.info('Multiple events can be logged')

// ❌ Avoid in tight loops
for (let i = 0; i < 10000; i++) {
  logger.debug(`Processing ${i}`)  // Too many logs!
}
```

---

## 🔒 Security

### Never Log Sensitive Data

```python
# ❌ NEVER
logger.info("Login", password=password)
logger.info("Payment", card_number=card)
logger.info("API call", api_key=key)

# ✅ SAFE
logger.info("Login", email=email)
logger.info("Payment", last_4=card[-4:])
logger.info("API call", endpoint="/users")
```

---

## 🐛 Debugging Tips

### Trace a Request End-to-End

1. Look for the session_id in backend logs
2. Search frontend logs with same session_id
3. All related logs share the same session_id

### Find Slow Operations

Backend:
```bash
jq 'select(.duration_seconds > 1)' logs/app.json.log
```

Frontend: Look for console logs with `duration_ms > 1000`

### Debug Production Issues

1. Get session_id from user (shown in error messages)
2. Search backend logs: `grep "session_id" logs/app.log`
3. Reconstruct the entire user journey

---

## 📚 Need More?

- **Full Integration Guide**: See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- **Project Context**: See [CLAUDE.md](./CLAUDE.md)
- **Progress Tracking**: See [progress.md](./progress.md)

---

## 🎉 You're All Set!

Your application now has:
- ✅ Comprehensive logging on backend and frontend
- ✅ Automatic session tracking
- ✅ Error boundary for React errors
- ✅ Performance monitoring
- ✅ End-to-end request correlation

Start logging and enjoy better observability! 🚀
