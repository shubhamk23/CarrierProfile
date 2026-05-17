"""
Comprehensive Logging System for Backend
Supports structured JSON logging with session tracking
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback
from contextvars import ContextVar
import uuid

# Context variable for session/request tracking
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add session tracking information
        session_id = session_id_var.get()
        request_id = request_id_var.get()
        user_id = user_id_var.get()

        if session_id:
            log_data['session_id'] = session_id
        if request_id:
            log_data['request_id'] = request_id
        if user_id:
            log_data['user_id'] = user_id

        # Add exception information if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields if provided
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Get session info
        session_id = session_id_var.get()
        request_id = request_id_var.get()

        session_info = ""
        if request_id:
            session_info = f" [req:{request_id[:8]}]"
        if session_id:
            session_info += f" [ses:{session_id[:8]}]"

        # Build log message
        log_msg = f"{color}{timestamp} [{record.levelname:8}]{reset} {record.name} - {record.getMessage()}{session_info}"

        # Add exception info if present
        if record.exc_info:
            log_msg += f"\n{color}{''.join(traceback.format_exception(*record.exc_info))}{reset}"

        return log_msg


class AppLogger:
    """Main application logger with session tracking"""

    def __init__(
        self,
        name: str = "carrier_profile",
        log_level: str = "INFO",
        log_dir: Optional[Path] = None,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_json: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.handlers.clear()  # Clear existing handlers

        # Create logs directory if needed
        if enable_file and log_dir:
            log_dir.mkdir(parents=True, exist_ok=True)

        # Console handler with colored output
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(ColoredFormatter())
            self.logger.addHandler(console_handler)

        # File handler with JSON formatting
        if enable_file and enable_json and log_dir:
            json_handler = logging.FileHandler(log_dir / 'app.json.log')
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(json_handler)

        # File handler with text formatting
        if enable_file and log_dir:
            text_handler = logging.FileHandler(log_dir / 'app.log')
            text_handler.setLevel(logging.DEBUG)
            text_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)8s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            text_handler.setFormatter(text_formatter)
            self.logger.addHandler(text_handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def _log(self, level: int, message: str, **extra_fields):
        """Internal log method with extra fields support"""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None
        )
        if extra_fields:
            record.extra_fields = extra_fields
        self.logger.handle(record)

    def debug(self, message: str, **extra_fields):
        """Log debug message"""
        self._log(logging.DEBUG, message, **extra_fields)

    def info(self, message: str, **extra_fields):
        """Log info message"""
        self._log(logging.INFO, message, **extra_fields)

    def warning(self, message: str, **extra_fields):
        """Log warning message"""
        self._log(logging.WARNING, message, **extra_fields)

    def error(self, message: str, exc_info: bool = False, **extra_fields):
        """Log error message"""
        if exc_info:
            self.logger.error(message, exc_info=True, extra=extra_fields if extra_fields else None)
        else:
            self._log(logging.ERROR, message, **extra_fields)

    def critical(self, message: str, exc_info: bool = False, **extra_fields):
        """Log critical message"""
        if exc_info:
            self.logger.critical(message, exc_info=True, extra=extra_fields if extra_fields else None)
        else:
            self._log(logging.CRITICAL, message, **extra_fields)

    def exception(self, message: str, **extra_fields):
        """Log exception with traceback"""
        self.logger.exception(message, extra=extra_fields if extra_fields else None)


# Session tracking utilities
def set_session_id(session_id: str):
    """Set session ID for current context"""
    session_id_var.set(session_id)


def get_session_id() -> Optional[str]:
    """Get current session ID"""
    return session_id_var.get()


def set_request_id(request_id: str):
    """Set request ID for current context"""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_var.get()


def set_user_id(user_id: str):
    """Set user ID for current context"""
    user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """Get current user ID"""
    return user_id_var.get()


def generate_session_id() -> str:
    """Generate a new session ID"""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """Generate a new request ID"""
    return str(uuid.uuid4())


# Create default logger instance
from pathlib import Path
import os

log_dir = Path(__file__).parent.parent.parent / 'logs'
log_level = os.getenv('LOG_LEVEL', 'INFO')

logger = AppLogger(
    name="carrier_profile",
    log_level=log_level,
    log_dir=log_dir,
    enable_console=True,
    enable_file=True,
    enable_json=True
)

__all__ = [
    'logger',
    'AppLogger',
    'set_session_id',
    'get_session_id',
    'set_request_id',
    'get_request_id',
    'set_user_id',
    'get_user_id',
    'generate_session_id',
    'generate_request_id',
]
