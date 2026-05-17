"""
Backend Logging Examples
Demonstrates various logging patterns and best practices
"""

from fastapi import APIRouter, HTTPException, Request
from app.utils.logger import logger, set_user_id, get_session_id
from typing import Optional

router = APIRouter(prefix="/examples", tags=["examples"])


# Example 1: Basic Logging
@router.get("/basic")
async def basic_logging_example():
    """Simple logging example"""
    logger.info("Processing basic request")
    logger.debug("This only shows in DEBUG mode")

    return {"status": "success"}


# Example 2: Logging with Context
@router.get("/with-context")
async def logging_with_context(user_id: str, action: str):
    """Logging with additional context fields"""
    logger.info(
        "User action recorded",
        user_id=user_id,
        action=action,
        timestamp=datetime.utcnow().isoformat()
    )

    return {"status": "logged"}


# Example 3: Error Logging
@router.post("/error-handling")
async def error_handling_example(data: dict):
    """Proper error logging"""
    try:
        # Simulate some processing
        if not data.get("valid"):
            raise ValueError("Invalid data provided")

        result = process_data(data)
        logger.info("Data processed successfully", record_count=len(result))

        return {"result": result}

    except ValueError as e:
        # Log validation errors at WARNING level
        logger.warning(
            f"Validation error: {str(e)}",
            data_keys=list(data.keys()),
            exc_info=False  # No stack trace for validation errors
        )
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Log unexpected errors at ERROR level with full traceback
        logger.error(
            "Unexpected error processing data",
            data_keys=list(data.keys()),
            exc_info=True  # Include stack trace
        )
        raise HTTPException(status_code=500, detail="Internal server error")


# Example 4: Session Tracking
@router.post("/login")
async def login_example(email: str, request: Request):
    """Track user session after login"""
    # Authenticate user (simplified)
    user_id = authenticate_user(email)

    # Set user ID in context - all subsequent logs will include it
    set_user_id(user_id)

    # Get current session ID
    session_id = get_session_id()

    logger.info(
        "User logged in",
        user_id=user_id,
        email=email,
        ip_address=request.client.host if request.client else "unknown"
    )

    return {
        "user_id": user_id,
        "session_id": session_id
    }


# Example 5: Performance Logging
@router.get("/performance")
async def performance_logging_example():
    """Log performance metrics"""
    import time

    start_time = time.time()

    # Simulate expensive operation
    result = expensive_operation()

    duration = time.time() - start_time

    # Log with performance metrics
    logger.info(
        "Expensive operation completed",
        duration_seconds=round(duration, 4),
        result_size=len(result),
        operation="expensive_operation"
    )

    # Warn if too slow
    if duration > 1.0:
        logger.warning(
            "Slow operation detected",
            duration_seconds=round(duration, 4),
            threshold=1.0
        )

    return {"duration": duration, "result": result}


# Example 6: Structured Logging for Analytics
@router.post("/analytics-event")
async def analytics_event_example(event_type: str, properties: dict):
    """Log structured analytics events"""
    logger.info(
        f"Analytics event: {event_type}",
        event_type=event_type,
        event_properties=properties,
        source="user_action",
        category="analytics"
    )

    return {"tracked": True}


# Example 7: Multi-step Operation Logging
@router.post("/multi-step")
async def multi_step_logging_example(data: dict):
    """Log multiple steps of a complex operation"""
    operation_id = generate_operation_id()

    logger.info(
        "Starting multi-step operation",
        operation_id=operation_id,
        step="start"
    )

    try:
        # Step 1
        logger.debug("Step 1: Validating data", operation_id=operation_id, step=1)
        validated_data = validate(data)

        # Step 2
        logger.debug("Step 2: Processing data", operation_id=operation_id, step=2)
        processed_data = process(validated_data)

        # Step 3
        logger.debug("Step 3: Saving results", operation_id=operation_id, step=3)
        result = save(processed_data)

        logger.info(
            "Multi-step operation completed",
            operation_id=operation_id,
            step="complete",
            total_steps=3
        )

        return {"result": result, "operation_id": operation_id}

    except Exception as e:
        logger.error(
            "Multi-step operation failed",
            operation_id=operation_id,
            step="error",
            exc_info=True
        )
        raise


# Example 8: Database Operation Logging
@router.get("/database/{record_id}")
async def database_logging_example(record_id: str):
    """Log database operations"""
    logger.debug(f"Fetching record from database", record_id=record_id)

    try:
        # Simulate database query
        record = await db.fetch_record(record_id)

        if not record:
            logger.warning(
                "Record not found",
                record_id=record_id,
                table="records"
            )
            raise HTTPException(status_code=404, detail="Record not found")

        logger.info(
            "Record fetched successfully",
            record_id=record_id,
            record_type=record.get("type")
        )

        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Database query failed",
            record_id=record_id,
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Database error")


# Helper functions (simplified for examples)
def process_data(data):
    return [{"processed": True}]

def authenticate_user(email):
    return f"user_{hash(email) % 10000}"

def generate_operation_id():
    import uuid
    return str(uuid.uuid4())

def expensive_operation():
    import time
    time.sleep(0.1)
    return ["result1", "result2"]

def validate(data):
    return data

def process(data):
    return data

def save(data):
    return {"id": "123", "saved": True}


# Import at module level
from datetime import datetime
