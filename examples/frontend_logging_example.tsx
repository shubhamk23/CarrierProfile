/**
 * Frontend Logging Examples
 * Demonstrates various logging patterns and best practices
 */

'use client';

import React, { useState, useEffect } from 'react';
import logger from '@/utils/logger';
import apiClient from '@/utils/api-client';
import {
  useComponentLogger,
  usePageView,
  usePerformanceLogger,
  useUserActionLogger,
} from '@/hooks/useLogger';

// Example 1: Basic Component Logging
export function BasicLoggingExample() {
  // Automatically logs mount/unmount
  useComponentLogger('BasicLoggingExample');

  // Log page view
  usePageView('Basic Logging Example');

  return <div>Basic logging enabled</div>;
}

// Example 2: User Action Logging
export function UserActionExample() {
  const { logAction } = useUserActionLogger();

  const handleButtonClick = (buttonName: string) => {
    logAction('button_clicked', {
      button: buttonName,
      timestamp: new Date().toISOString(),
    });
  };

  const handleFormSubmit = (data: any) => {
    logAction('form_submitted', {
      form_type: 'contact',
      fields: Object.keys(data),
    });

    logger.info('Form data validated', 'FormSubmit', {
      field_count: Object.keys(data).length,
    });
  };

  return (
    <div>
      <button onClick={() => handleButtonClick('primary')}>
        Primary Action
      </button>
      <button onClick={() => handleButtonClick('secondary')}>
        Secondary Action
      </button>
    </div>
  );
}

// Example 3: API Call Logging
export function ApiCallExample() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      // API call is automatically logged by apiClient
      const response = await apiClient.get('/api/users');

      logger.info('Data fetched successfully', 'ApiCall', {
        record_count: response.data.length,
      });

      setData(response.data);
    } catch (err) {
      // Error is automatically logged by apiClient
      const error = err as Error;
      setError(error);

      logger.error('Failed to fetch data', 'ApiCall', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={fetchData} disabled={loading}>
        {loading ? 'Loading...' : 'Fetch Data'}
      </button>
      {error && <p>Error: {error.message}</p>}
    </div>
  );
}

// Example 4: Performance Tracking
export function PerformanceExample() {
  const { trackPerformance } = usePerformanceLogger();

  const heavyComputation = () => {
    trackPerformance('heavy_computation', () => {
      // Simulate expensive operation
      let result = 0;
      for (let i = 0; i < 1000000; i++) {
        result += Math.sqrt(i);
      }
      return result;
    });
  };

  const asyncOperation = async () => {
    await trackPerformance('async_operation', async () => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      return 'completed';
    });
  };

  return (
    <div>
      <button onClick={heavyComputation}>Run Heavy Computation</button>
      <button onClick={asyncOperation}>Run Async Operation</button>
    </div>
  );
}

// Example 5: Error Handling with Logging
export function ErrorHandlingExample() {
  const [count, setCount] = useState(0);

  const riskyOperation = () => {
    try {
      if (count > 5) {
        throw new Error('Count exceeded maximum value');
      }

      setCount(count + 1);
      logger.debug('Count incremented', 'Counter', { count: count + 1 });
    } catch (error) {
      logger.error('Risky operation failed', 'Counter', error as Error);

      // Show user-friendly message
      alert('Operation failed. Please try again.');
    }
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={riskyOperation}>Increment (max 5)</button>
    </div>
  );
}

// Example 6: Lifecycle Logging
export function LifecycleExample() {
  const [data, setData] = useState(null);

  useEffect(() => {
    logger.info('Component mounted', 'Lifecycle');

    // Fetch initial data
    fetchInitialData();

    return () => {
      logger.info('Component will unmount', 'Lifecycle');
    };
  }, []);

  useEffect(() => {
    if (data) {
      logger.debug('Data updated', 'Lifecycle', { hasData: !!data });
    }
  }, [data]);

  const fetchInitialData = async () => {
    logger.debug('Fetching initial data', 'Lifecycle');

    try {
      const response = await apiClient.get('/api/initial-data');
      setData(response.data);

      logger.info('Initial data loaded', 'Lifecycle', {
        data_size: JSON.stringify(response.data).length,
      });
    } catch (error) {
      logger.error('Failed to load initial data', 'Lifecycle', error as Error);
    }
  };

  return <div>Lifecycle logging enabled</div>;
}

// Example 7: Multi-step Process Logging
export function MultiStepExample() {
  const [step, setStep] = useState(1);

  const processStep = async (stepNumber: number) => {
    logger.info(`Starting step ${stepNumber}`, 'MultiStep', { step: stepNumber });

    try {
      // Simulate processing
      await new Promise(resolve => setTimeout(resolve, 500));

      logger.info(`Completed step ${stepNumber}`, 'MultiStep', { step: stepNumber });

      if (stepNumber < 3) {
        setStep(stepNumber + 1);
      } else {
        logger.info('All steps completed', 'MultiStep', { total_steps: 3 });
      }
    } catch (error) {
      logger.error(`Step ${stepNumber} failed`, 'MultiStep', error as Error);
    }
  };

  return (
    <div>
      <p>Current Step: {step}</p>
      <button onClick={() => processStep(step)}>
        Process Step {step}
      </button>
    </div>
  );
}

// Example 8: Custom Timer Logging
export function CustomTimerExample() {
  const executeWithTiming = () => {
    // Manual timer
    const endTimer = logger.startTimer('custom_operation');

    // Perform operation
    setTimeout(() => {
      // Some logic here
      logger.info('Operation completed', 'CustomTimer');

      // End timer (logs duration automatically)
      endTimer();
    }, 1000);
  };

  return (
    <button onClick={executeWithTiming}>
      Execute Timed Operation
    </button>
  );
}

// Example 9: Conditional Logging
export function ConditionalLoggingExample() {
  const debugMode = process.env.NODE_ENV === 'development';

  const handleAction = () => {
    // Always log important events
    logger.info('User performed action', 'Action');

    // Conditionally log debug info
    if (debugMode) {
      logger.debug('Debug information', 'Action', {
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
      });
    }
  };

  return <button onClick={handleAction}>Perform Action</button>;
}

// Example 10: Comprehensive Form Example
export function FormLoggingExample() {
  const [formData, setFormData] = useState({ name: '', email: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    logger.debug('Validating form', 'Form', { fields: Object.keys(formData) });

    const newErrors: Record<string, string> = {};

    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    if (!formData.email) {
      newErrors.email = 'Email is required';
    }

    if (Object.keys(newErrors).length > 0) {
      logger.warn('Form validation failed', 'Form', {
        errors: Object.keys(newErrors),
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    logger.logUserAction('form_submit_attempted', { form_type: 'contact' });

    if (!validateForm()) {
      return;
    }

    try {
      const response = await apiClient.post('/api/contact', formData);

      logger.info('Form submitted successfully', 'Form', {
        response_id: response.data.id,
      });

      // Reset form
      setFormData({ name: '', email: '' });
      alert('Form submitted successfully!');
    } catch (error) {
      logger.error('Form submission failed', 'Form', error as Error);
      alert('Submission failed. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        placeholder="Name"
      />
      {errors.name && <span>{errors.name}</span>}

      <input
        type="email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
      />
      {errors.email && <span>{errors.email}</span>}

      <button type="submit">Submit</button>
    </form>
  );
}

// Main example page component
export default function LoggingExamplesPage() {
  usePageView('Logging Examples');

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Frontend Logging Examples</h1>

      <div className="space-y-8">
        <section>
          <h2 className="text-2xl font-semibold mb-4">1. Basic Logging</h2>
          <BasicLoggingExample />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">2. User Actions</h2>
          <UserActionExample />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">3. API Calls</h2>
          <ApiCallExample />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">4. Performance Tracking</h2>
          <PerformanceExample />
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4">5. Error Handling</h2>
          <ErrorHandlingExample />
        </section>
      </div>
    </div>
  );
}
