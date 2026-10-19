import React from 'react';
import { ShieldCheck } from 'lucide-react';

/**
 * Sovereign Mode badge — prominent indicator that system is running locally.
 */
export default function SovereignBadge({ mode }) {
  const label = mode || 'SOVEREIGN MODE';
  return (
    <div className="sovereign-badge">
      <span className="sovereign-dot" />
      <ShieldCheck size={14} />
      {label}
    </div>
  );
}
