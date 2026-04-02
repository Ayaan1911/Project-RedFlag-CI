import { useNavigate } from 'react-router-dom'
import { formatTimestamp } from '../../utils/scoring'

const MOCK_RECENT_SCANS = [
  { repo: 'redflag-ci-vulnerable-dataset', pr: '#1', score: 87, criticals: 3, highs: 2, mediums: 4, timestamp: new Date().toISOString(), isReal: true, repoId: '1199052310' },
  { repo: 'Shivam-64bit/fintech-payment-engine', pr: '#3', score: 45, criticals: 1, highs: 1, mediums: 3, timestamp: new Date(Date.now() - 15 * 60000).toISOString() },
  { repo: 'Shivam-64bit/auth-microservice', pr: '#1', score: 12, criticals: 0, highs: 0, mediums: 1, timestamp: new Date(Date.now() - 42 * 60000).toISOString() },
  { repo: 'Shivam-64bit/legacy-java-crm', pr: '#5', score: 68, criticals: 2, highs: 3, mediums: 1, timestamp: new Date(Date.now() - 115 * 60000).toISOString() },
  { repo: 'Shivam-64bit/banking-app-v2', pr: '#2', score: 5, criticals: 0, highs: 0, mediums: 0, timestamp: new Date(Date.now() - 340 * 60000).toISOString() },
]

export default function ScanTable() {
  const navigate = useNavigate()

  return (
    <div className="glass-1 table-card w-full overflow-x-auto">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-section-title text-textPrimary tracking-tight">Recent Scans</h3>
      </div>
      
      <table className="w-full text-left border-collapse z-10 relative">
        <thead>
          <tr>
            <th className="table-header-row pt-2 pl-4">Repository</th>
            <th className="table-header-row pt-2">Pull Request</th>
            <th className="table-header-row pt-2">Vibe Score</th>
            <th className="table-header-row pt-2">Findings</th>
            <th className="table-header-row pt-2 text-right pr-4">Time</th>
          </tr>
        </thead>
        <tbody>
          {MOCK_RECENT_SCANS.map((scan, i) => {
            // Vibe Score Coloring
            const s = scan.score
            const scoreColor = s >= 80 ? 'score-high' : s >= 60 ? 'score-medium' : 'score-low'
            
            return (
              <tr 
                key={scan.pr} 
                onClick={() => {
                  if (scan.isReal) {
                    navigate(`/repo/${scan.repoId}/scan/${scan.pr.replace('#', '')}`)
                  } else {
                    navigate(`/scan/demo/${scan.pr.replace('#', '')}`)
                  }
                }}
                className="table-body-row cursor-pointer"
                style={{ '--i': i }}
              >
                {/* Repository */}
                <td className="align-middle pl-4">
                  <span className="repo-name">{scan.repo}</span>
                </td>

                {/* Pull Request */}
                <td className="align-middle">
                  <span className="pr-id bg-[rgba(107,142,255,0.08)] px-2 py-0.5 rounded-md border border-[rgba(107,142,255,0.15)]">
                    {scan.pr}
                  </span>
                </td>

                {/* Vibe Score */}
                <td className="align-middle vibe-score">
                  <span className={`num ${scoreColor}`}>{scan.score}</span>
                  <span className="den ml-[1px]">/100</span>
                </td>

                {/* Findings Badges */}
                <td className="align-middle flex items-center gap-1.5 h-[48px]">
                  <span className={`badge ${scan.criticals > 0 ? 'badge-critical' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.criticals}
                  </span>
                  <span className={`badge ${scan.highs > 0 ? 'badge-high' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.highs}
                  </span>
                  <span className={`badge ${scan.mediums > 0 ? 'badge-medium' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.mediums}
                  </span>
                </td>

                {/* Time */}
                <td className="align-middle text-right pr-4">
                  <span className="time-ago">
                    {formatTimestamp(scan.timestamp)}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
