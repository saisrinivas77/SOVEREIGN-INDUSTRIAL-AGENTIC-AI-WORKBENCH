import React from 'react';
import StatusBadge from './StatusBadge';
import { formatTimestamp, formatDuration } from '../../utils/formatters';

/**
 * Vertical execution timeline for agent trace steps.
 * Every step is backend-provided — never fabricated.
 */
export default function Timeline({ steps }) {
  if (!steps || steps.length === 0) {
    return (
      <div className="state-container" style={{ padding: 'var(--space-8)' }}>
        <p className="state-message">No execution steps recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="timeline">
      {steps.map((step, idx) => (
        <div className="timeline-item animate-fade-in" key={step.step_id || idx} style={{ animationDelay: `${idx * 50}ms` }}>
          <div className={`timeline-dot timeline-dot--${(step.status || 'queued').toLowerCase()}`} />
          <div className="timeline-content">
            <div className="timeline-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
                <span className="timeline-meta">#{step.step_number ?? idx + 1}</span>
                <span className="timeline-action">{step.action || 'Unknown Action'}</span>
              </div>
              <StatusBadge status={step.status} />
            </div>

            <div style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap', marginBottom: 'var(--space-1)' }}>
              {step.tool && (
                <span className="timeline-meta">
                  Tool: <span style={{ color: 'var(--color-text-accent)' }}>{step.tool}</span>
                </span>
              )}
              {step.timestamp && (
                <span className="timeline-meta">{formatTimestamp(step.timestamp)}</span>
              )}
              {step.duration != null && (
                <span className="timeline-meta">{formatDuration(step.duration)}</span>
              )}
            </div>

            {step.result_summary && (
              <div className="timeline-detail">{step.result_summary}</div>
            )}

            {step.error && step.status === 'FAILED' && (
              <div className="timeline-detail" style={{ color: 'var(--color-status-failed)', marginTop: 'var(--space-1)' }}>
                {step.error}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
