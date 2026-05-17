/**
 * Comprehensive Frontend Logging System
 * Supports structured logging with session tracking
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL',
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: string;
  sessionId?: string;
  requestId?: string;
  userId?: string;
  url?: string;
  userAgent?: string;
  extra?: Record<string, any>;
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
}

export interface LoggerConfig {
  minLevel: LogLevel;
  enableConsole: boolean;
  enableRemote: boolean;
  remoteEndpoint?: string;
  batchSize?: number;
  batchInterval?: number;
  enablePerformanceTracking?: boolean;
}

class Logger {
  private config: LoggerConfig;
  private sessionId: string;
  private logQueue: LogEntry[] = [];
  private batchTimer: NodeJS.Timeout | null = null;

  private static instance: Logger;

  private constructor(config: Partial<LoggerConfig> = {}) {
    this.config = {
      minLevel: LogLevel.INFO,
      enableConsole: true,
      enableRemote: false,
      batchSize: 10,
      batchInterval: 5000,
      enablePerformanceTracking: true,
      ...config,
    };

    // Initialize session ID
    this.sessionId = this.getOrCreateSessionId();

    // Start batch timer if remote logging is enabled
    if (this.config.enableRemote) {
      this.startBatchTimer();
    }

    // Capture unhandled errors
    if (typeof window !== 'undefined') {
      window.addEventListener('error', this.handleGlobalError.bind(this));
      window.addEventListener('unhandledrejection', this.handleUnhandledRejection.bind(this));
    }
  }

  public static getInstance(config?: Partial<LoggerConfig>): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger(config);
    }
    return Logger.instance;
  }

  private getOrCreateSessionId(): string {
    if (typeof window === 'undefined') {
      return 'server-' + this.generateId();
    }

    let sessionId = sessionStorage.getItem('app_session_id');
    if (!sessionId) {
      sessionId = this.generateId();
      sessionStorage.setItem('app_session_id', sessionId);
    }
    return sessionId;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  public generateRequestId(): string {
    return this.generateId();
  }

  private shouldLog(level: LogLevel): boolean {
    const levels = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.CRITICAL];
    const minLevelIndex = levels.indexOf(this.config.minLevel);
    const currentLevelIndex = levels.indexOf(level);
    return currentLevelIndex >= minLevelIndex;
  }

  private createLogEntry(
    level: LogLevel,
    message: string,
    context?: string,
    extra?: Record<string, any>,
    error?: Error
  ): LogEntry {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      sessionId: this.sessionId,
      extra,
    };

    // Add browser context if available
    if (typeof window !== 'undefined') {
      entry.url = window.location.href;
      entry.userAgent = navigator.userAgent;
    }

    // Add error details if present
    if (error) {
      entry.error = {
        name: error.name,
        message: error.message,
        stack: error.stack,
      };
    }

    return entry;
  }

  private formatConsoleMessage(entry: LogEntry): string {
    const { timestamp, level, context, message, sessionId, requestId } = entry;
    const time = new Date(timestamp).toLocaleTimeString();
    const ctx = context ? `[${context}]` : '';
    const session = sessionId ? `[ses:${sessionId.slice(0, 8)}]` : '';
    const request = requestId ? `[req:${requestId.slice(0, 8)}]` : '';
    return `${time} ${level} ${ctx}${session}${request} ${message}`;
  }

  private logToConsole(entry: LogEntry): void {
    if (!this.config.enableConsole) return;

    const formattedMessage = this.formatConsoleMessage(entry);

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(formattedMessage, entry.extra || '');
        break;
      case LogLevel.INFO:
        console.info(formattedMessage, entry.extra || '');
        break;
      case LogLevel.WARN:
        console.warn(formattedMessage, entry.extra || '');
        break;
      case LogLevel.ERROR:
      case LogLevel.CRITICAL:
        console.error(formattedMessage, entry.error || entry.extra || '');
        if (entry.error?.stack) {
          console.error(entry.error.stack);
        }
        break;
    }
  }

  private async sendToRemote(entries: LogEntry[]): Promise<void> {
    if (!this.config.enableRemote || !this.config.remoteEndpoint) return;

    try {
      await fetch(this.config.remoteEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ logs: entries }),
      });
    } catch (error) {
      console.error('Failed to send logs to remote endpoint:', error);
    }
  }

  private startBatchTimer(): void {
    if (this.batchTimer) {
      clearInterval(this.batchTimer);
    }

    this.batchTimer = setInterval(() => {
      this.flushLogs();
    }, this.config.batchInterval);
  }

  private async flushLogs(): Promise<void> {
    if (this.logQueue.length === 0) return;

    const logsToSend = [...this.logQueue];
    this.logQueue = [];

    await this.sendToRemote(logsToSend);
  }

  private log(
    level: LogLevel,
    message: string,
    context?: string,
    extra?: Record<string, any>,
    error?: Error
  ): void {
    if (!this.shouldLog(level)) return;

    const entry = this.createLogEntry(level, message, context, extra, error);

    // Log to console
    this.logToConsole(entry);

    // Add to queue for remote logging
    if (this.config.enableRemote) {
      this.logQueue.push(entry);

      // Flush if batch size reached
      if (this.logQueue.length >= (this.config.batchSize || 10)) {
        this.flushLogs();
      }
    }
  }

  // Public logging methods
  public debug(message: string, context?: string, extra?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, context, extra);
  }

  public info(message: string, context?: string, extra?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, context, extra);
  }

  public warn(message: string, context?: string, extra?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, context, extra);
  }

  public error(message: string, context?: string, error?: Error | Record<string, any>): void {
    const errorObj = error instanceof Error ? error : undefined;
    const extra = error && !(error instanceof Error) ? error : undefined;
    this.log(LogLevel.ERROR, message, context, extra, errorObj);
  }

  public critical(message: string, context?: string, error?: Error | Record<string, any>): void {
    const errorObj = error instanceof Error ? error : undefined;
    const extra = error && !(error instanceof Error) ? error : undefined;
    this.log(LogLevel.CRITICAL, message, context, extra, errorObj);
  }

  // Performance tracking
  public startTimer(label: string): () => void {
    if (!this.config.enablePerformanceTracking) {
      return () => {};
    }

    const startTime = performance.now();
    return () => {
      const duration = performance.now() - startTime;
      this.info(`Performance: ${label}`, 'Performance', {
        duration_ms: Math.round(duration),
        label,
      });
    };
  }

  // API call tracking
  public logApiCall(
    method: string,
    url: string,
    statusCode?: number,
    duration?: number,
    error?: Error
  ): void {
    const message = `API ${method} ${url}`;
    const extra = {
      method,
      url,
      statusCode,
      duration_ms: duration ? Math.round(duration) : undefined,
    };

    if (error) {
      this.error(message, 'API', error);
    } else if (statusCode && statusCode >= 400) {
      this.warn(message, 'API', extra);
    } else {
      this.info(message, 'API', extra);
    }
  }

  // User action tracking
  public logUserAction(action: string, details?: Record<string, any>): void {
    this.info(`User action: ${action}`, 'UserAction', details);
  }

  // Page view tracking
  public logPageView(path: string, title?: string): void {
    this.info(`Page view: ${path}`, 'PageView', { path, title });
  }

  // Global error handlers
  private handleGlobalError(event: ErrorEvent): void {
    this.error(
      `Uncaught error: ${event.message}`,
      'GlobalError',
      new Error(event.message)
    );
  }

  private handleUnhandledRejection(event: PromiseRejectionEvent): void {
    this.error(
      `Unhandled promise rejection: ${event.reason}`,
      'UnhandledRejection',
      event.reason instanceof Error ? event.reason : new Error(String(event.reason))
    );
  }

  // Cleanup
  public destroy(): void {
    if (this.batchTimer) {
      clearInterval(this.batchTimer);
      this.batchTimer = null;
    }
    this.flushLogs();
  }

  // Get session info
  public getSessionId(): string {
    return this.sessionId;
  }
}

// Create and export singleton instance
export const logger = Logger.getInstance({
  minLevel: process.env.NODE_ENV === 'production' ? LogLevel.INFO : LogLevel.DEBUG,
  enableConsole: true,
  enableRemote: process.env.NODE_ENV === 'production',
  remoteEndpoint: process.env.NEXT_PUBLIC_LOG_ENDPOINT || '/api/logs',
});

export default logger;
