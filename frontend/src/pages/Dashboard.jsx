import { useEffect, useState } from 'react'
import Navbar from '../components/shared/Navbar'
import DashboardHero from '../components/dashboard/DashboardHero'
import MetricCards from '../components/dashboard/MetricCards'
import VibeDebtChart from '../components/dashboard/VibeDebtChart'
import RouterSavingsCard from '../components/dashboard/RouterSavingsCard'
import LiveActivityFeed from '../components/dashboard/LiveActivityFeed'
import ScanTable from '../components/dashboard/ScanTable'
import { getScans } from '../api/client'

const DEFAULT_REPO_ID = import.meta.env.VITE_DEFAULT_REPO_ID || '1199052310'

export default function Dashboard() {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadScans() {
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

    loadScans()
  }, [])

  if (loading) {
    return <div className="min-h-screen bg-[var(--bg-root)] text-[var(--text-primary)] flex items-center justify-center">Loading dashboard...</div>
  }

  if (error) {
    return <div className="min-h-screen bg-[var(--bg-root)] text-red flex items-center justify-center">Error: {error}</div>
  }

  return (
    <div className="min-h-screen relative p-8 pb-10 flex justify-center">
      <div className="dashboard-shell w-full max-w-[1280px] flex flex-col overflow-hidden">
        <Navbar />

        <main className="p-[28px_32px] flex flex-col gap-5">
          <section style={{ '--i': 0 }}>
            <DashboardHero />
          </section>

          <section className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5" style={{ '--i': 1 }}>
            <MetricCards />
          </section>

          <section className="grid grid-cols-1 lg:grid-cols-11 gap-4 min-h-[380px]" style={{ '--i': 2 }}>
            <div className="lg:col-span-5 h-full">
              <VibeDebtChart />
            </div>
            <div className="lg:col-span-3 h-full">
              <RouterSavingsCard />
            </div>
            <div className="lg:col-span-3 h-full">
              <LiveActivityFeed />
            </div>
          </section>

          <section style={{ '--i': 3 }}>
            <ScanTable scans={scans} />
          </section>
        </main>
      </div>
    </div>
  )
}
