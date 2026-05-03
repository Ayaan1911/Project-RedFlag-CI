import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import RepoDetail from './pages/RepoDetail'
import ScanDetail from './pages/ScanDetail'
import CodeDiffViewer from './pages/CodeDiffViewer'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/repo/:repoId" element={<RepoDetail />} />
        <Route path="/scan/:repoId/:prNumber" element={<ScanDetail />} />
        <Route path="/repo/:repoId/scan/:prNumber" element={<ScanDetail />} />
        <Route path="/diff/:repoId/:prNumber/:findingIndex" element={<CodeDiffViewer />} />
      </Routes>
    </BrowserRouter>
  )
}
