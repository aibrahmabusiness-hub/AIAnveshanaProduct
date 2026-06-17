import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Project from './pages/Project';
import Dashboard from './pages/Dashboard';
import { WorkflowVersionProvider } from './contexts/WorkflowVersionContext';

export default function App() {
  return (
    <WorkflowVersionProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/v2-dashboard" element={<Dashboard />} />
          <Route path="/v2-canvas" element={<Project />} />
          <Route path="*" element={<Navigate to="/v2-dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </WorkflowVersionProvider>
  );
}
