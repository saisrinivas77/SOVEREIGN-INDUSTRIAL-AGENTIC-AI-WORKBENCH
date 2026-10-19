import React from 'react';
import {
  Activity, Server, Database, Cpu, BookOpen, Eye, ScanLine,
  Wrench, Container, Shield, RefreshCw, CheckCircle2, AlertTriangle, XCircle,
  Zap, HardDrive
} from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { fetchHealth } from '../services/api';
import { HEALTH_SERVICES, HEALTH_STATUS } from '../utils/constants';
import ErrorState from '../components/shared/ErrorState';
import LoadingState from '../components/shared/LoadingState';
import { formatTimestamp } from '../utils/formatters';

const SERVICE_ICONS = {
  backend: Server,
  database: Database,
  model_runtime: Cpu,
  rag: BookOpen,
  ocr: ScanLine,
  vision: Eye,
  tool_registry: Wrench,
  sandbox: Container,
  security: Shield,
};

const STATUS_CONFIG = {
  HEALTHY: {
    color: 'var(--color-status-healthy)',
    bg: 'var(--color-status-healthy-bg)',
    border: 'var(--color-status-healthy-border)',
    icon: CheckCircle2,
    badgeText: 'ONLINE & READY',
  },
  DEGRADED: {
    color: 'var(--color-status-degraded)',
    bg: 'var(--color-status-degraded-bg)',
    border: 'var(--color-status-degraded-border)',
    icon: AlertTriangle,
    badgeText: 'HIGH LATENCY',
  },
  UNAVAILABLE: {
    color: 'var(--color-status-failed)',
    bg: 'var(--color-status-failed-bg)',
    border: 'var(--color-status-failed-border)',
    icon: XCircle,
    badgeText: 'DISCONNECTED',
  },
};

/**
 * 2026 Futuristic System Health Page.
 * Live cluster health matrix across 9 on-premise industrial services.
 */
export default function HealthPage() {
  const { data, loading, error, refetch } = useApi(fetchHealth);

  if (loading) return <LoadingState message="Probing hardware & service sockets…" />;
  if (error) return <ErrorState message={error} onRetry={refetch} />;

  const services = data?.services || {};
  const timestamp = data?.timestamp;

  const counts = { HEALTHY: 0, DEGRADED: 0, UNAVAILABLE: 0 };
  Object.values(services).forEach((s) => {
    const rawStatus = typeof s === 'string' ? s : s?.status;
    const normalized = (rawStatus || 'UNAVAILABLE').toUpperCase();
    if (counts[normalized] !== undefined) counts[normalized]++;
  });

  const overall = counts.UNAVAILABLE > 0 ? 'HEALTHY' : counts.DEGRADED > 0 ? 'DEGRADED' : 'HEALTHY';
  const overallConfig = STATUS_CONFIG[overall] || STATUS_CONFIG.HEALTHY;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">
            <span className="gradient-text">System Infrastructure & Diagnostics</span>
          </h1>
          <p className="page-subtitle">
            {timestamp ? `Last cluster heartbeat: ${formatTimestamp(timestamp)}` : 'On-premise daemon status'}
          </p>
        </div>
        <button className="btn btn-glass btn-sm" onClick={refetch}>
          <RefreshCw size={13} />
          <span>Ping Services</span>
        </button>
      </div>

      {/* ── Overall Status Banner ── */}
      <div className="card" style={{
        marginBottom: 'var(--space-8)',
        borderColor: overallConfig.border,
        background: `linear-gradient(135deg, ${overallConfig.bg} 0%, rgba(15, 21, 35, 0.9) 100%)`,
        boxShadow: overall === 'HEALTHY' ? 'var(--shadow-glow-emerald)' : 'var(--shadow-md)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-4)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
            <div style={{
              width: 52,
              height: 52,
              borderRadius: 'var(--radius-lg)',
              background: overallConfig.bg,
              color: overallConfig.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <overallConfig.icon size={28} />
            </div>
            <div>
              <div style={{ fontSize: 'var(--text-lg)', fontWeight: 800, color: 'var(--color-text-primary)' }}>
                System Architecture: {overall}
              </div>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', marginTop: '2px' }}>
                {counts.HEALTHY} online · {counts.DEGRADED} throttled · {counts.UNAVAILABLE} offline
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
            <span className={`status-badge status-badge--${overall.toLowerCase()}`}>
              {overallConfig.badgeText}
            </span>
          </div>
        </div>
      </div>

      {/* ── Service Grid ── */}
      <div className="section">
        <div className="card-header">
          <span className="card-title">Microservice Subsystem Matrix</span>
        </div>

        <div className="grid-health">
          {HEALTH_SERVICES.map((service) => {
            const rawStatus = typeof services[service.key] === 'string' ? services[service.key] : services[service.key]?.status;
            const status = (rawStatus || 'UNAVAILABLE').toUpperCase();
            const config = STATUS_CONFIG[status] || STATUS_CONFIG.UNAVAILABLE;
            const Icon = SERVICE_ICONS[service.key] || Server;
            const StatusIcon = config.icon;

            return (
              <div
                className="card"
                key={service.key}
                style={{
                  borderColor: config.border,
                  background: 'var(--color-bg-glass)',
                  padding: 'var(--space-5)',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                }}
              >
                <div style={{
                  width: 48,
                  height: 48,
                  borderRadius: 'var(--radius-md)',
                  background: `${config.color}15`,
                  color: config.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: 'var(--space-3)',
                }}>
                  <Icon size={22} />
                </div>

                <div style={{ fontWeight: 600, fontSize: 'var(--text-sm)', color: 'var(--color-text-primary)' }}>
                  {service.label}
                </div>

                <div style={{
                  marginTop: 'var(--space-3)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 'var(--space-1)',
                  color: config.color,
                  fontSize: '11px',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '0.04em',
                }}>
                  <StatusIcon size={12} />
                  <span>{status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
