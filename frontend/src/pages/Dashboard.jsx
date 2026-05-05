import { useEffect, useState } from 'react'
import Navbar from '../components/shared/Navbar'
import ScanTable from '../components/dashboard/ScanTable'
import { getScans } from '../api/client'

const DEFAULT_REPO_ID = import.meta.env.VITE_DEFAULT_REPO_ID || '1199052310'

export default function Dashboard() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadScans = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getScans(DEFAULT_REPO_ID)
      setScans(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadScans()
  }, [])

  if (loading) {
    return <div className="min-h-screen bg-[var(--bg-root)] text-[var(--text-primary)] flex items-center justify-center">Loading dashboard...</div>
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[var(--bg-root)] text-red flex flex-col items-center justify-center gap-4">
        <div>Error: {error}</div>
        <button onClick={loadScans} className="bg-surface border border-border px-4 py-2 rounded-lg hover:text-text transition-colors">Retry</button>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative p-8 pb-10 flex justify-center bg-[var(--bg-root)] text-[var(--text-primary)] font-body">
      <div className="dashboard-shell w-full max-w-[1280px] flex flex-col overflow-hidden">
        <Navbar />

        <main className="p-[28px_32px] flex flex-col gap-8">
          <section className="flex flex-col gap-2">
            <h1 style={{ font: '700 32px var(--font-display)', color: '#F0F2FF', letterSpacing: '-0.5px' }}>RedFlag CI</h1>
            <p style={{ font: '400 15px var(--font-body)', color: '#9AA0BC' }}>AI-powered security scanner for GitHub Pull Requests</p>
            <div className="mt-2 text-[14px] text-[#4A5070] font-mono">
              Total scans: <span className="text-[#6B8EFF] font-bold">{scans.length}</span>
            </div>
          </section>

          <section className="w-full">
            <ScanTable scans={scans} />
          </section>
        </main>
      </div>
    </div>
  )
}
