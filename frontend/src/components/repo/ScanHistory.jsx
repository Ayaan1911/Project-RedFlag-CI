import { useNavigate } from 'react-router-dom'
import { MOCK_SCAN_HISTORY } from '../../api/repoMockData'
import { getScoreColor, formatTimestamp } from '../../utils/scoring'

export default function ScanHistory() {
  const navigate = useNavigate()

  const statusConfig = {
    passed: { label: 'Passed', bg: 'bg-greenDim', text: 'text-green', icon: '✓' },
    warning: { label: 'Warning', bg: 'bg-amberDim', text: 'text-amber', icon: '⚠' },
    failed: { label: 'Failed', bg: 'bg-redDim', text: 'text-red', icon: '✕' },
  }

  return (
    <div className="glass-1 overflow-hidden">
      <div className="px-5 py-4 border-b border-border">
        <h3 className="text-sm font-medium text-text">Scan History</h3>
      </div>
      <div className="divide-y divide-border/50">
        {MOCK_SCAN_HISTORY.map((scan) => {
          const sc = statusConfig[scan.status]
          return (
            <button
              key={scan.pr}
              onClick={() => navigate(`/scan/demo/${scan.pr.replace('#', '')}`)}
              className="w-full text-left px-5 py-3 hover:bg-surface transition-colors flex items-center gap-4"
            >
              {/* Status dot */}
              <span className={`w-8 h-8 rounded-lg ${sc.bg} flex items-center justify-center text-sm ${sc.text}`}>
                {sc.icon}
              </span>

              {/* PR info */}
              <div className="flex-1 min-w-0">
                <div className="text-sm text-text font-medium">PR {scan.pr}</div>
                <div className="text-xs text-textMuted mt-0.5">
                  {scan.findings} findings · {scan.criticals} critical
                </div>
              </div>

              {/* Score */}
              <div className="text-right">
                <div className={`text-lg font-bold ${getScoreColor(scan.score)}`}>{scan.score}</div>
                <div className="text-[11px] text-textMuted">{formatTimestamp(scan.timestamp)}</div>
              </div>

              {/* Status badge */}
              <span className={`text-xs px-2.5 py-1 rounded-full ${sc.bg} ${sc.text} font-medium`}>
                {sc.label}
              </span>

              <span className="text-textDim text-xs">→</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
