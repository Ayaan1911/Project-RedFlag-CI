import Navbar from '../components/shared/Navbar'
import ParticleBackground from '../components/shared/ParticleBackground'
import GradientOrb from '../components/shared/GradientOrb'
import RepoHeader from '../components/repo/RepoHeader'
import WAFScoreCard from '../components/repo/WAFScoreCard'
import FinOpsCard from '../components/repo/FinOpsCard'
import CompliancePosture from '../components/repo/CompliancePosture'
import VulnerabilityLifecycle from '../components/repo/VulnerabilityLifecycle'
import ScanHistory from '../components/repo/ScanHistory'

export default function RepoDetail() {
  return (
    <div className="min-h-screen bg-bg relative">
      <ParticleBackground />
      <GradientOrb />

      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />

        <main className="max-w-[1440px] mx-auto px-6 py-6 flex flex-col gap-5 flex-1 w-full">
          {/* Repo Header */}
          <RepoHeader />

          {/* Row 1: WAF + FinOps */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <WAFScoreCard />
            <FinOpsCard />
          </div>

          {/* Compliance Posture */}
          <CompliancePosture />

          {/* Vulnerability Lifecycle */}
          <VulnerabilityLifecycle />

          {/* Scan History */}
          <ScanHistory />
        </main>
      </div>
    </div>
  )
}
