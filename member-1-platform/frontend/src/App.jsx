import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import DashboardPage from './pages/DashboardPage';
import WorkbenchPage from './pages/WorkbenchPage';
import DocumentsPage from './pages/DocumentsPage';
import KnowledgePage from './pages/KnowledgePage';
import TracePage from './pages/TracePage';
import ArtifactsPage from './pages/ArtifactsPage';
import SecurityPage from './pages/SecurityPage';
import ModelsPage from './pages/ModelsPage';
import HealthPage from './pages/HealthPage';

/**
 * Sovereign AI Workbench — Main Application
 * 9 pages, all data from backend /api/v1/*
 */
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="workbench" element={<WorkbenchPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="knowledge" element={<KnowledgePage />} />
          <Route path="trace" element={<TracePage />} />
          <Route path="artifacts" element={<ArtifactsPage />} />
          <Route path="security" element={<SecurityPage />} />
          <Route path="models" element={<ModelsPage />} />
          <Route path="health" element={<HealthPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
