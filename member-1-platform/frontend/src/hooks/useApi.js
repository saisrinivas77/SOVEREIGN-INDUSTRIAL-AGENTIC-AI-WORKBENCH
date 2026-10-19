import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Generic data fetching hook.
 * Handles loading, error, and data states.
 * Initial load sets loading state; background refetches update data seamlessly without UI flashing.
 */
export function useApi(fetchFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const hasLoadedRef = useRef(false);

  const execute = useCallback(async (options = {}) => {
    const isSilent = options?.silent ?? hasLoadedRef.current;
    
    if (!isSilent) {
      setLoading(true);
    }
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
      hasLoadedRef.current = true;
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    hasLoadedRef.current = false;
    execute({ silent: false });
  }, [execute]);

  const refetch = useCallback((options = { silent: true }) => {
    return execute(options);
  }, [execute]);

  return { data, loading, error, refetch };
}
