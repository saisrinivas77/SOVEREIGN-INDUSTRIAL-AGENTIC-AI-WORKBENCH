import { useState, useEffect, useRef, useCallback } from 'react';
import { POLL_INTERVAL, TERMINAL_STATES } from '../utils/constants';

/**
 * Polling hook for real-time status updates.
 * Automatically stops on terminal states.
 * 
 * @param {Function} fetchFn - Async function to poll
 * @param {Object} options
 * @param {number} options.interval - Poll interval in ms (default: POLL_INTERVAL)
 * @param {boolean} options.enabled - Whether polling is active
 * @param {Function} options.isTerminal - Check if data is in terminal state
 * @returns {{ data, loading, error, isPolling }}
 */
export function usePolling(fetchFn, options = {}) {
  const {
    interval = POLL_INTERVAL,
    enabled = true,
    isTerminal = () => false,
  } = options;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPolling, setIsPolling] = useState(false);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);

  const poll = useCallback(async () => {
    try {
      const result = await fetchFn();
      if (!mountedRef.current) return;
      
      setData(result);
      setError(null);
      setLoading(false);

      // Stop polling on terminal state
      if (isTerminal(result)) {
        setIsPolling(false);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err.message || 'Polling failed');
      setLoading(false);
    }
  }, [fetchFn, isTerminal]);

  useEffect(() => {
    mountedRef.current = true;

    if (!enabled) {
      setIsPolling(false);
      return;
    }

    // Initial fetch
    poll();
    setIsPolling(true);

    // Start interval
    intervalRef.current = setInterval(poll, interval);

    return () => {
      mountedRef.current = false;
      setIsPolling(false);
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, interval, poll]);

  return { data, loading, error, isPolling };
}
