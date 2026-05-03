import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import Navbar from '../components/shared/Navbar'
import RepoBanner from '../components/repo/RepoBanner'
import WAFScoreCard from '../components/repo/WAFScoreCard'
import FinOpsCostCard from '../components/repo/FinOpsCostCard'
import CompliancePosture from '../components/repo/CompliancePosture'
import VulnerabilityLifecycle from '../components/repo/VulnerabilityLifecycle'
import RepoScanHistoryTable from '../components/repo/RepoScanHistoryTable'
import FindingExpandable from '../components/scan/FindingExpandable'
import { getRepoDetail } from '../api/client'

export default function RepoDetail() {
  const { repoId } = useParams()
  const [repoData, setRepoData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadRepoDetail() {
      try {
        setLoading(true)
        setError(null)
        const data = await getRepoDetail(repoId)
        setRepoData(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadRepoDetail()
  }, [repoId])

  const normalizedFindings = useMemo(() => {
    if (!repoData?.findings) return []
    return repoData.findings.map((finding, index) => ({
      id: `${finding.file || 'finding'}-${finding.line || 0}-${index}`,
      type: finding.type,
      severity: finding.severity,
      file: finding.file,
      line: finding.line,
      description: finding.description,
      exploitPayload: finding.exploit_payload ? [
        `Payload: ${finding.exploit_payload.payload || ''}`,
        `Impact: ${finding.exploit_payload.impact || ''}`,
        `Curl: ${finding.exploit_payload.curl_example || ''}`,
      ].join('\n') : null,
      rootCause: finding.root_cause ? {
        pattern: finding.root_cause.llm_behavioral_pattern || 'Root cause',
        description: finding.root_cause.why_llm_generated_this || '',
      } : null,
      fixCode: finding.fix_code || '',
      complianceViolations: finding.compliance_violations || [],
      auditImpact: finding.audit_impact || '',
      prNumber: repoData.latestScan?.pr_number || 0,
      scanDate: repoData.latestScan?.timestamp || null,
    }))
  }, [repoData])

  if (loading) return <div className="min-h-screen bg-[var(--bg-root)] text-[var(--text-primary)] flex items-center justify-center">Loading repository data...</div>
  if (error) return <div className="min-h-screen bg-[var(--bg-root)] text-red flex items-center justify-center">Error: {error}</div>
  if (!repoData) return <div className="min-h-screen bg-[var(--bg-root)] text-[var(--text-primary)] flex items-center justify-center">No repository data found.</div>

  return (
    <div className="min-h-screen relative p-8 pb-10 flex justify-center bg-[var(--bg-root)] text-[var(--text-primary)] font-body">
      <div className="dashboard-shell w-full max-w-[1280px] flex flex-col overflow-hidden">
        <Navbar />

        <main className="p-[28px_32px] flex flex-col gap-6">
          <section className="repo-section" style={{ '--i': 0 }}>
            <RepoBanner repo={repoData.repo} />
          </section>

          <section className="repo-section grid grid-cols-1 lg:grid-cols-2 gap-5" style={{ '--i': 1 }}>
            <WAFScoreCard data={repoData.wafScores} />
            <FinOpsCostCard data={repoData.costBreakdown} />
          </section>

          <section className="repo-section" style={{ '--i': 2 }}>
            <CompliancePosture data={repoData.complianceSummary} />
          </section>

          <section className="repo-section grid grid-cols-1 lg:grid-cols-2 gap-5" style={{ '--i': 3 }}>
            <VulnerabilityLifecycle findings={normalizedFindings} scanHistory={repoData.scans} />
            <RepoScanHistoryTable scans={repoData.scans} />
          </section>

          <section className="repo-section" style={{ '--i': 4 }}>
            <FindingExpandable findings={normalizedFindings} />
          </section>
        </main>
      </div>
    </div>
  )
}
