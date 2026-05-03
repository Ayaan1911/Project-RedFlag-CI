import { useNavigate } from 'react-router-dom'
import { formatTimestamp } from '../../utils/scoring'

export default function ScanTable({ scans = [] }) {
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
          {scans.map((scan, i) => {
            const scoreColor = scan.vibe_risk_score >= 80 ? 'score-high' : scan.vibe_risk_score >= 60 ? 'score-medium' : 'score-low'
            const isClickable = Boolean(scan.repo_id && scan.pr_number)

            return (
              <tr
                key={`${scan.repo_id}-${scan.pr_number}`}
                onClick={() => {
                  if (isClickable) {
                    navigate(`/scan/${scan.repo_id}/${scan.pr_number}`)
                  }
                }}
                className={`table-body-row ${isClickable ? 'cursor-pointer' : ''}`}
                style={{ '--i': i }}
              >
                <td className="align-middle pl-4">
                  <span className="repo-name">{scan.repo_full_name || scan.repo_id}</span>
                </td>

                <td className="align-middle">
                  <span className="pr-id bg-[rgba(107,142,255,0.08)] px-2 py-0.5 rounded-md border border-[rgba(107,142,255,0.15)]">
                    #{scan.pr_number}
                  </span>
                </td>

                <td className="align-middle vibe-score">
                  <span className={`num ${scoreColor}`}>{scan.vibe_risk_score}</span>
                  <span className="den ml-[1px]">/100</span>
                </td>

                <td className="align-middle flex items-center gap-1.5 h-[48px]">
                  <span className={`badge ${(scan.findings_summary?.critical || 0) > 0 ? 'badge-critical' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.findings_summary?.critical || 0}
                  </span>
                  <span className={`badge ${(scan.findings_summary?.high || 0) > 0 ? 'badge-high' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.findings_summary?.high || 0}
                  </span>
                  <span className={`badge ${(scan.findings_summary?.medium || 0) > 0 ? 'badge-medium' : 'opacity-40 grayscale border-[rgba(255,255,255,0.1)] text-textMuted bg-[rgba(255,255,255,0.02)]'}`}>
                    {scan.findings_summary?.medium || 0}
                  </span>
                </td>

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
