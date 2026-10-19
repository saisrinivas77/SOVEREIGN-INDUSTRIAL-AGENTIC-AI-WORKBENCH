import React from 'react';
import { useLocation } from 'react-router-dom';
import { ShieldCheck, Cpu, Bell, Activity } from 'lucide-react';
import { NAV_ITEMS } from '../../utils/constants';
import { useApi } from '../../hooks/useApi';
import { fetchHealth } from '../../services/api';

/**
 * Futuristic 2026 TopBar with Live Sovereign Node Status and Breadcrumbs.
 */
export default function TopBar() {
  const location = useLocation();
  const currentNav = NAV_ITEMS.find(
    (item) => item.path === location.pathname
  ) || NAV_ITEMS[0];

  const { data: health } = useApi(fetchHealth);

  const overallStatus = React.useMemo(() => {
    if (!health || !health.services) return 'UNKNOWN';
    const statuses = Object.values(health.services).map((s) =>
      (typeof s === 'string' ? s : s?.status || 'HEALTHY').toUpperCase()
    );
    if (statuses.some((s) => s === 'UNAVAILABLE')) return 'DEGRADED';
    if (statuses.every((s) => s === 'HEALTHY')) return 'HEALTHY';
    return 'HEALTHY';
  }, [health]);

  return (
    <header className="topbar">
      {/* ── Breadcrumb ── */}
      <div className="topbar-breadcrumb">
        <span className="topbar-section">Workbench</span>
        <span className="topbar-separator">/</span>
        <span className="topbar-page">{currentNav.label}</span>
      </div>

      {/* ── Live Sovereign Node Telemetry ── */}
      <div className="topbar-actions">
        <div className="node-status-pill" title="Hardware Execution: Local GPU/NPU">
          <span className="node-status-dot" />
          <span>SOVEREIGN CLUSTER</span>
          <span style={{ opacity: 0.5, margin: '0 2px' }}>|</span>
          <span style={{ color: 'var(--color-text-secondary)', fontSize: '11px' }}>
            {overallStatus}
          </span>
        </div>
      </div>
    </header>
  );
}
