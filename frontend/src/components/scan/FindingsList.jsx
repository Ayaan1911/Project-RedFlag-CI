import { useParams, useNavigate } from 'react-router-dom'
import SeverityBadge from '../shared/SeverityBadge'

export default function FindingsList({ findings = [], onSelectFinding }) {
  const { repoId = 'demo', prNumber = '42' } = useParams()
  const navigate = useNavigate()

  const handleKeyDown = (event, finding) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      onSelectFinding(finding)
    }
  }

  return (
    <div className="glass-1 overflow-hidden">
      <div className="px-5 py-4 border-b border-border flex items-center justify-between">
        <h3 className="text-sm font-medium text-text">All Findings ({findings.length})</h3>
        <span className="text-xs text-textMuted">Click to expand</span>
      </div>
      <div className="divide-y divide-border/50">
        {findings.map((finding, i) => (
          <div
            key={i}
            role="button"
            tabIndex={0}
            onClick={() => onSelectFinding(finding)}
            onKeyDown={(event) => handleKeyDown(event, finding)}
            className="w-full text-left px-5 py-3 hover:bg-surface transition-colors flex items-center gap-4 cursor-pointer"
          >
            <SeverityBadge severity={finding.severity} />
            <div className="flex-1 min-w-0">
              <div className="text-sm text-text truncate">{finding.description}</div>
              <div className="text-xs text-textMuted mt-0.5">
                {finding.file}:{finding.line} · {finding.type}
              </div>
            </div>
            <div className="flex gap-1 shrink-0">
              {finding.exploit_payload && (
                <span className="text-[10px] text-red bg-redDim px-1.5 py-0.5 rounded">💥</span>
              )}
              {finding.root_cause && (
                <span className="text-[10px] text-purple bg-purple/10 px-1.5 py-0.5 rounded">🧠</span>
              )}
              {finding.compliance_violations && finding.compliance_violations.length > 0 && (
                <span className="text-[10px] text-amber bg-amberDim px-1.5 py-0.5 rounded">🛡️</span>
              )}
            </div>
            <button
              onClick={(event) => {
                event.stopPropagation()
                navigate(`/diff/${repoId}/${prNumber}/${i}`)
              }}
              style={{
                background: 'transparent',
                border: '1px solid #E63946',
                color: '#E63946',
                padding: '4px 12px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontFamily: 'monospace',
                fontSize: '12px',
              }}
              className="ml-4 hover:bg-red/10 transition-colors"
            >
              View Diff →
            </button>
            <span className="text-textDim text-xs ml-2">→</span>
          </div>
        ))}
      </div>
    </div>
  )
}
