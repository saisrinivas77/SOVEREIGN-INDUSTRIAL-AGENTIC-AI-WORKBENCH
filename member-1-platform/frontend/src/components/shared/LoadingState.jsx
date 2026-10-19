import React from 'react';

/**
 * Loading state with spinner and optional message.
 */
export default function LoadingState({ message }) {
  return (
    <div className="state-container">
      <div className="spinner spinner--lg" style={{ marginBottom: 'var(--space-4)' }} />
      <p className="state-message">{message || 'Loading…'}</p>
    </div>
  );
}
