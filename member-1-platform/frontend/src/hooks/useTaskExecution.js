import { useState, useCallback } from 'react';
import { createTask, fetchTask, fetchTaskTrace, fetchTaskArtifacts } from '../services/api';
import { usePolling } from './usePolling';
import { TERMINAL_STATES } from '../utils/constants';

/**
 * Task lifecycle hook: create → poll → inspect.
 * Manages the complete task execution flow.
 */
export function useTaskExecution() {
  const [activeTaskId, setActiveTaskId] = useState(null);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState(null);

  // Poll task status
  const {
    data: taskData,
    loading: taskLoading,
    error: taskError,
    isPolling,
  } = usePolling(
    () => fetchTask(activeTaskId),
    {
      enabled: !!activeTaskId,
      isTerminal: (data) => data && TERMINAL_STATES.has(data.status),
    }
  );

  // Poll trace
  const {
    data: traceData,
    loading: traceLoading,
  } = usePolling(
    () => fetchTaskTrace(activeTaskId),
    {
      enabled: !!activeTaskId,
      interval: 2500,
      isTerminal: (data) => taskData && TERMINAL_STATES.has(taskData.status),
    }
  );

  // Start a new task
  const startTask = useCallback(async (instruction, files) => {
    setCreating(true);
    setCreateError(null);
    try {
      const result = await createTask({ instruction, files });
      setActiveTaskId(result.task_id || result.id);
      return result;
    } catch (err) {
      setCreateError(err.message);
      throw err;
    } finally {
      setCreating(false);
    }
  }, []);

  // Clear active task
  const clearTask = useCallback(() => {
    setActiveTaskId(null);
    setCreateError(null);
  }, []);

  return {
    activeTaskId,
    startTask,
    clearTask,
    creating,
    createError,
    taskData,
    taskLoading,
    taskError,
    traceData,
    traceLoading,
    isPolling,
  };
}
