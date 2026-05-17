"""
Logs API Router
Endpoint to receive logs from frontend
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.utils.logger import logger

router = APIRouter(prefix="/logs", tags=["logs"])


class FrontendLogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    context: Optional[str] = None
    sessionId: Optional[str] = Field(None, alias="sessionId")
    requestId: Optional[str] = Field(None, alias="requestId")
    userId: Optional[str] = Field(None, alias="userId")
    url: Optional[str] = None
    userAgent: Optional[str] = Field(None, alias="userAgent")
    extra: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True


class LogBatchRequest(BaseModel):
    logs: List[FrontendLogEntry]


@router.post("/", status_code=201)
async def receive_frontend_logs(
    request: Request,
    log_batch: LogBatchRequest
):
    """
    Receive and process logs from frontend
    """
    try:
        for log_entry in log_batch.logs:
            # Map frontend log levels to Python log levels
            level_mapping = {
                'DEBUG': 'debug',
                'INFO': 'info',
                'WARN': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'critical'
            }

            log_method = getattr(logger, level_mapping.get(log_entry.level, 'info'))

            # Prepare extra fields
            extra_fields = {
                'source': 'frontend',
                'frontend_timestamp': log_entry.timestamp,
                'context': log_entry.context,
                'url': log_entry.url,
                'user_agent': log_entry.userAgent,
            }

            if log_entry.extra:
                extra_fields.update(log_entry.extra)

            if log_entry.error:
                extra_fields['error'] = log_entry.error

            # Log the frontend entry
            message = f"[Frontend] {log_entry.message}"
            log_method(message, **extra_fields)

        logger.info(
            f"Received {len(log_batch.logs)} log entries from frontend",
            batch_size=len(log_batch.logs)
        )

        return {
            "status": "success",
            "received": len(log_batch.logs)
        }

    except Exception as e:
        logger.error(f"Failed to process frontend logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process logs")


@router.get("/health")
async def logs_health_check():
    """Health check endpoint for logging service"""
    return {
        "status": "healthy",
        "service": "logging",
        "timestamp": datetime.utcnow().isoformat()
    }
