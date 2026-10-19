import React from 'react';

/**
 * Dashboard metric card with icon, value, and label.
 * Value comes from backend — never hardcoded.
 */
export default function MetricCard({ icon: Icon, value, label, color, loading }) {
  const iconBg = color ? `${color}18` : 'var(--color-accent-primary-subtle)';
  const iconColor = color || 'var(--color-accent-primary)';

  return (
    <div className="card metric-card">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <div className="card-value">
            {loading ? (
              <span style={{ color: 'var(--color-text-tertiary)', fontSize: 'var(--text-lg)' }}>—</span>
            ) : (
              value ?? '—'
            )}
          </div>
          <div className="metric-label">{label}</div>
        </div>
        {Icon && (
          <div
            className="metric-icon"
            style={{ background: iconBg, color: iconColor }}
          >
            <Icon size={18} />
          </div>
        )}
      </div>
    </div>
  );
}
