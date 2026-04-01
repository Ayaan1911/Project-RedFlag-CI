import Navbar from '../components/shared/Navbar'
import DashboardHero from '../components/dashboard/DashboardHero'
import MetricCards from '../components/dashboard/MetricCards'
import VibeDebtChart from '../components/dashboard/VibeDebtChart'
import RouterSavingsCard from '../components/dashboard/RouterSavingsCard'
import LiveActivityFeed from '../components/dashboard/LiveActivityFeed'
import ScanTable from '../components/dashboard/ScanTable'

export default function Dashboard() {
  return (
    <div className="min-h-screen relative p-8 pb-10 flex justify-center">
      {/* Dashboard shell container matching Resq.io exactly */}
      <div className="dashboard-shell w-full max-w-[1280px] flex flex-col overflow-hidden">
        {/* Row 1: Navbar */}
        <Navbar />

        {/* Padding container for the grid layout */}
        <main className="p-[28px_32px] flex flex-col gap-5">
          {/* Row 2: Hero Banner */}
          <section style={{ '--i': 0 }}>
            <DashboardHero />
          </section>

          {/* Row 3: 6 Metric Cards Row */}
          <section className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5" style={{ '--i': 1 }}>
            <MetricCards />
          </section>

          {/* Row 4: Main Data Row (5:3:3) */}
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

          {/* Row 5: Recent Scans */}
          <section style={{ '--i': 3 }}>
            <ScanTable />
          </section>
        </main>
      </div>
    </div>
  )
}
