import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { WorkflowVersionProvider } from './contexts/WorkflowVersionContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <WorkflowVersionProvider>
      <App />
    </WorkflowVersionProvider>
  </StrictMode>,
)
