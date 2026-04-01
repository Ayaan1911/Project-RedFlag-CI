import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import RepoDetail from './pages/RepoDetail'
import ScanDetail from './pages/ScanDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/repo/:repoId" element={<RepoDetail />} />
        <Route path="/scan/:repoId/:prNumber" element={<ScanDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
