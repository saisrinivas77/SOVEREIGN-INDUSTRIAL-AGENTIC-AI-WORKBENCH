import React from 'react';
import { Inbox } from 'lucide-react';

/**
 * Empty state display for pages with no data.
 */
export default function EmptyState({ icon: Icon = Inbox, title, message }) {
  return (
    <div className="state-container animate-fade-in">
      <div className="state-icon">
        <Icon size={48} />
      </div>
      {title && <h3 className="state-title">{title}</h3>}
      <p className="state-message">{message || 'No data available.'}</p>
    </div>
  );
}
