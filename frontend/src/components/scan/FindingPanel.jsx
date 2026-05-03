import SeverityBadge from '../shared/SeverityBadge'

export default function FindingPanel({ finding, onClose }) {
  if (!finding) return null

  return (
    <div className="absolute right-0 top-0 h-full w-[420px] bg-surface border-l border-border z-50 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-surface border-b border-border px-5 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SeverityBadge severity={finding.severity} />
          <span className="text-sm font-medium text-text">{finding.type}</span>
        </div>
        <button
          onClick={onClose}
          className="w-7 h-7 rounded-lg bg-surfaceAlt border border-border flex items-center justify-center text-textMuted hover:text-text hover:bg-bg transition-colors text-xs"
        >
          ✕
        </button>
      </div>

      <div className="p-5 space-y-5">
        {/* Location */}
        <div>
          <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2">Location</h4>
          <div className="bg-bg rounded-lg px-3 py-2 border border-border text-sm">
            <span className="text-textMuted">📄</span>{' '}
            <span className="text-text">{finding.file}</span>
            <span className="text-textDim">:{finding.line}</span>
          </div>
        </div>

        {/* Description */}
        <div>
          <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2">Description</h4>
          <p className="text-sm text-text leading-relaxed">{finding.description}</p>
        </div>

        {/* Fix */}
        {finding.fix_code && (
          <div>
            <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2">AI Fix</h4>
            <pre className="bg-bg rounded-lg px-4 py-3 border border-border text-xs text-green overflow-x-auto whitespace-pre-wrap font-mono">
              {finding.fix_code}
            </pre>
          </div>
        )}

        {/* Exploit Payload */}
        {finding.exploit_payload && (
          <div>
            <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="text-red">💥</span> Exploit Payload
            </h4>
            <div className="bg-bg rounded-lg border border-red/20 p-4 space-y-3">
              <div>
                <span className="text-[11px] text-textDim">Payload</span>
                <pre className="text-xs text-red font-mono mt-1 whitespace-pre-wrap">{finding.exploit_payload.payload}</pre>
              </div>
              <div>
                <span className="text-[11px] text-textDim">Impact</span>
                <p className="text-xs text-text mt-1">{finding.exploit_payload.impact}</p>
              </div>
              <div>
                <span className="text-[11px] text-textDim">cURL Example</span>
                <pre className="text-xs text-amber font-mono mt-1 whitespace-pre-wrap bg-amberDim/30 rounded px-2 py-1">{finding.exploit_payload.curl_example}</pre>
              </div>
            </div>
          </div>
        )}

        {/* Root Cause */}
        {finding.root_cause && (
          <div>
            <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="text-purple">🧠</span> Root Cause Analysis
            </h4>
            <div className="bg-bg rounded-lg border border-purple/20 p-4 space-y-3">
              <div>
                <span className="text-[11px] text-textDim">Why LLM Generated This</span>
                <p className="text-xs text-text mt-1">{finding.root_cause.why_llm_generated_this}</p>
              </div>
              <div>
                <span className="text-[11px] text-textDim">Behavioral Pattern</span>
                <span className="inline-block mt-1 text-xs text-purple bg-purple/10 px-2 py-0.5 rounded-full">
                  {finding.root_cause.llm_behavioral_pattern}
                </span>
              </div>
              <div>
                <span className="text-[11px] text-textDim">Developer Mistake</span>
                <p className="text-xs text-text mt-1">{finding.root_cause.developer_mistake}</p>
              </div>
              <div>
                <span className="text-[11px] text-textDim">How to Avoid</span>
                <pre className="text-xs text-green font-mono mt-1 whitespace-pre-wrap">{finding.root_cause.how_to_avoid}</pre>
              </div>
            </div>
          </div>
        )}

        {/* Compliance Violations */}
        {finding.compliance_violations && finding.compliance_violations.length > 0 && (
          <div>
            <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="text-amber">🛡️</span> Compliance Violations
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {finding.compliance_violations.map((v, i) => (
                <span key={i} className="text-xs bg-amberDim text-amber px-2 py-0.5 rounded-full">
                  {v}
                </span>
              ))}
            </div>
            {finding.audit_impact && (
              <p className="text-xs text-textMuted mt-2 leading-relaxed">{finding.audit_impact}</p>
            )}
          </div>
        )}

        {/* Reputation (for package findings) */}
        {finding.reputation && (
          <div>
            <h4 className="text-xs text-textMuted uppercase tracking-wider mb-2 flex items-center gap-2">
              <span className="text-red">📦</span> Package Reputation
            </h4>
            <div className="bg-bg rounded-lg border border-red/20 p-4 grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-textDim">Trust Level</span>
                <div className="text-red font-medium mt-0.5">{finding.reputation.trust_level}</div>
              </div>
              <div>
                <span className="text-textDim">Downloads/week</span>
                <div className="text-text font-medium mt-0.5">{finding.reputation.weekly_downloads}</div>
              </div>
              <div>
                <span className="text-textDim">Package Age</span>
                <div className="text-text font-medium mt-0.5">{finding.reputation.package_age_days}d</div>
              </div>
              <div>
                <span className="text-textDim">Has Repository</span>
                <div className={`font-medium mt-0.5 ${finding.reputation.has_repository ? 'text-green' : 'text-red'}`}>
                  {finding.reputation.has_repository ? 'Yes' : 'No'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
