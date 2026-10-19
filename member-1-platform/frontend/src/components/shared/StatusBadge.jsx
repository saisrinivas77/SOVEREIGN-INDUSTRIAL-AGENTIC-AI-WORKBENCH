import React from 'react';

/**
 * Status badge with colored dot and label.
 * Supports: HEALTHY, DEGRADED, UNAVAILABLE, QUEUED, RUNNING, COMPLETED, FAILED, DENIED
 */
export default function StatusBadge({ status }) {
  if (!status) return null;
  const normalized = status.toUpperCase();
  return (
    <span className={`status-badge status-badge--${normalized.toLowerCase()}`}>
      <span className="status-dot" />
      {normalized}
    </span>
  );
}
