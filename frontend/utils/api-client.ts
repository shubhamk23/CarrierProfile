/**
 * API Client with automatic logging
 * Tracks all API calls with session and request IDs
 */

import logger from './logger';

export interface ApiClientConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Headers;
  requestId?: string;
  sessionId?: string;
}

export class ApiClient {
  private config: ApiClientConfig;
  private sessionId: string;

  constructor(config: ApiClientConfig = {}) {
    this.config = {
      baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
      timeout: 30000,
      ...config,
    };
    this.sessionId = logger.getSessionId();
  }

  private async request<T = any>(
    method: string,
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.config.baseURL}${endpoint}`;
    const requestId = logger.generateRequestId();
    const startTime = performance.now();

    // Prepare headers
    const headers = new Headers({
      'Content-Type': 'application/json',
      'X-Session-ID': this.sessionId,
      'X-Request-ID': requestId,
      ...this.config.headers,
      ...(options.headers as Record<string, string>),
    });

    // Log request start
    logger.debug(`API Request: ${method} ${endpoint}`, 'ApiClient', {
      method,
      url,
      requestId,
    });

    try {
      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

      // Make request
      const response = await fetch(url, {
        ...options,
        method,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const duration = performance.now() - startTime;

      // Parse response
      let data: T;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = (await response.text()) as any;
      }

      // Extract tracking headers from response
      const responseRequestId = response.headers.get('X-Request-ID');
      const responseSessionId = response.headers.get('X-Session-ID');

      // Log response
      logger.logApiCall(
        method,
        endpoint,
        response.status,
        duration,
        response.ok ? undefined : new Error(`HTTP ${response.status}`)
      );

      if (!response.ok) {
        throw new ApiError(
          `API request failed: ${response.statusText}`,
          response.status,
          data
        );
      }

      return {
        data,
        status: response.status,
        statusText: response.statusText,
        headers: response.headers,
        requestId: responseRequestId || requestId,
        sessionId: responseSessionId || this.sessionId,
      };
    } catch (error) {
      const duration = performance.now() - startTime;

      // Log error
      if (error instanceof Error) {
        logger.error(
          `API request failed: ${method} ${endpoint}`,
          'ApiClient',
          error
        );
      }

      throw error;
    }
  }

  // HTTP methods
  public async get<T = any>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, options);
  }

  public async post<T = any>(
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, {
      ...options,
      body: JSON.stringify(data),
    });
  }

  public async put<T = any>(
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', endpoint, {
      ...options,
      body: JSON.stringify(data),
    });
  }

  public async patch<T = any>(
    endpoint: string,
    data?: any,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', endpoint, {
      ...options,
      body: JSON.stringify(data),
    });
  }

  public async delete<T = any>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', endpoint, options);
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Create and export default instance
export const apiClient = new ApiClient();

export default apiClient;
