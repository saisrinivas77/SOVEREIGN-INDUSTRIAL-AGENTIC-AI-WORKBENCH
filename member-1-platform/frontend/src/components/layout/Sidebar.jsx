import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Wrench, FileText, BookOpen, GitBranch,
  Package, Shield, Cpu, Activity, Hexagon, Plus,
  ChevronLeft, ChevronRight, User, Terminal
} from 'lucide-react';
import { NAV_ITEMS } from '../../utils/constants';
import SovereignBadge from '../shared/SovereignBadge';

const ICON_MAP = {
  LayoutDashboard, Wrench, FileText, BookOpen, GitBranch,
  Package, Shield, Cpu, Activity,
};

/**
 * Futuristic 2026 AI Workbench Sidebar.
 * Expandable/collapsible with micro-interactions & user node status.
 */
export default function Sidebar({ isCollapsed, onToggleCollapse }) {
  const navigate = useNavigate();

  return (
    <aside className={`sidebar ${isCollapsed ? 'sidebar--collapsed' : ''}`}>
      {/* ── Brand Header ── */}
      <div className="sidebar-header">
        <NavLink to="/" className="sidebar-brand">
          <div className="sidebar-logo-glow">
            <Hexagon size={22} strokeWidth={2} />
          </div>
          {!isCollapsed && (
            <div className="sidebar-brand-text">
              <span className="sidebar-brand-name">Sovereign AI</span>
              <span className="sidebar-brand-sub">Workbench v2.6</span>
            </div>
          )}
        </NavLink>

        <button
          className="btn-icon btn-sm"
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          style={{ marginLeft: isCollapsed ? 'auto' : 0 }}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* ── New Task Action ── */}
      <div className="sidebar-action-wrap">
        <button
          className="btn-new-task"
          onClick={() => navigate('/workbench')}
          title="New Task"
        >
          <Plus size={16} />
          {!isCollapsed && <span>New Task</span>}
        </button>
      </div>

      {/* ── Navigation Items ── */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = ICON_MAP[item.icon] || LayoutDashboard;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'sidebar-link--active' : ''}`
              }
              title={isCollapsed ? item.label : undefined}
            >
              <Icon size={18} className="sidebar-icon" style={{ flexShrink: 0 }} />
              {!isCollapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* ── Footer / User Profile ── */}
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div style={{ marginBottom: 'var(--space-2)' }}>
            <SovereignBadge />
          </div>
        )}

        <div className="sidebar-user-pill">
          <div className="sidebar-avatar">
            <Terminal size={16} />
          </div>
          {!isCollapsed && (
            <div className="sidebar-user-details" style={{ overflow: 'hidden' }}>
              <div style={{ fontSize: 'var(--text-xs)', fontWeight: 'var(--weight-bold)', color: 'var(--color-text-primary)' }} className="truncate">
                Node_01 (Industrial)
              </div>
              <div style={{ fontSize: '10px', color: 'var(--color-text-emerald)' }} className="truncate">
                ● 100% Air-Gapped
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
