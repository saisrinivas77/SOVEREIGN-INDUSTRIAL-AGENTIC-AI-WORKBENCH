import React from 'react';
import { AlertTriangle } from 'lucide-react';

/**
 * Error state display with safe error message and retry action.
 * Never displays stack traces or internal paths.
 */
export default function ErrorState({ message, onRetry }) {
  return (
    <div className="state-container animate-fade-in">
      <div className="state-icon">
        <AlertTriangle size={48} />
      </div>
      <h3 className="state-title">Unable to Load Data</h3>
      <p className="state-message">
        {message || 'An error occurred while communicating with the backend service.'}
      </p>
      {onRetry && (
        <div className="state-action">
          <button className="btn btn-secondary" onClick={onRetry}>
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
