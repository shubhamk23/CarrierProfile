/**
 * React hooks for logging
 */

import { useEffect, useCallback, useRef } from 'react';
import logger from '../utils/logger';

/**
 * Hook to log component lifecycle events
 */
export function useComponentLogger(componentName: string, logMount = true) {
  useEffect(() => {
    if (logMount) {
      logger.debug(`Component mounted: ${componentName}`, 'Component');
    }

    return () => {
      logger.debug(`Component unmounted: ${componentName}`, 'Component');
    };
  }, [componentName, logMount]);
}

/**
 * Hook to log page views
 */
export function usePageView(pageName: string) {
  useEffect(() => {
    logger.logPageView(window.location.pathname, pageName);
  }, [pageName]);
}

/**
 * Hook to track performance of operations
 */
export function usePerformanceLogger() {
  const trackPerformance = useCallback((label: string, fn: () => void | Promise<void>) => {
    const endTimer = logger.startTimer(label);
    const result = fn();

    if (result instanceof Promise) {
      return result.finally(() => endTimer());
    } else {
      endTimer();
      return result;
    }
  }, []);

  return { trackPerformance };
}

/**
 * Hook to log user actions
 */
export function useUserActionLogger() {
  const logAction = useCallback((action: string, details?: Record<string, any>) => {
    logger.logUserAction(action, details);
  }, []);

  return { logAction };
}

/**
 * Hook to track render count (useful for debugging)
 */
export function useRenderLogger(componentName: string, props?: Record<string, any>) {
  const renderCount = useRef(0);

  useEffect(() => {
    renderCount.current += 1;
    logger.debug(
      `${componentName} rendered`,
      'Render',
      {
        count: renderCount.current,
        props,
      }
    );
  });

  return renderCount.current;
}

/**
 * Hook to log errors
 */
export function useErrorLogger() {
  const logError = useCallback((error: Error, context?: string, extra?: Record<string, any>) => {
    logger.error(
      error.message,
      context || 'ErrorBoundary',
      error
    );
  }, []);

  return { logError };
}

export default {
  useComponentLogger,
  usePageView,
  usePerformanceLogger,
  useUserActionLogger,
  useRenderLogger,
  useErrorLogger,
};
