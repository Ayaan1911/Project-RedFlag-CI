import { useNavigate } from 'react-router-dom'
import Navbar from '../components/shared/Navbar'
import RepoBanner from '../components/repo/RepoBanner'
import WAFScoreCard from '../components/repo/WAFScoreCard'
import FinOpsCostCard from '../components/repo/FinOpsCostCard'
import CompliancePosture from '../components/repo/CompliancePosture'
import VulnerabilityLifecycle from '../components/repo/VulnerabilityLifecycle'
import RepoScanHistoryTable from '../components/repo/RepoScanHistoryTable'
import FindingExpandable from '../components/scan/FindingExpandable'

import { MOCK_FINDINGS } from '../api/repoMockData'

export default function RepoDetail() {
  return (
    <div className="min-h-screen relative p-8 pb-10 flex justify-center bg-[var(--bg-root)] text-[var(--text-primary)] font-body">
      <div className="dashboard-shell w-full max-w-[1280px] flex flex-col overflow-hidden">
        <Navbar />

        <main className="p-[28px_32px] flex flex-col gap-6">
          {/* SECTION 1: Repo Header Banner */}
          <section className="repo-section" style={{ '--i': 0 }}>
            <RepoBanner />
          </section>

          {/* SECTION 2: WAF + FinOps */}
          <section className="repo-section grid grid-cols-1 lg:grid-cols-2 gap-5" style={{ '--i': 1 }}>
            <WAFScoreCard />
            <FinOpsCostCard />
          </section>

          {/* SECTION 3: Compliance Posture */}
          <section className="repo-section" style={{ '--i': 2 }}>
            <CompliancePosture />
          </section>

          {/* SECTION 4: Vulnerability Lifecycle + Scan History */}
          <section className="repo-section grid grid-cols-1 lg:grid-cols-2 gap-5" style={{ '--i': 3 }}>
            <VulnerabilityLifecycle />
            <RepoScanHistoryTable />
          </section>

          {/* SECTION 5: Recent Findings Detail */}
          <section className="repo-section" style={{ '--i': 4 }}>
             <FindingExpandable findings={MOCK_FINDINGS} />
          </section>
        </main>
      </div>
    </div>
  )
}
