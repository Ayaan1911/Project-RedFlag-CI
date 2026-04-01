import { MOCK_SCAN_DETAIL } from '../../api/mockData'
import { getScoreColor, getRiskLabel } from '../../utils/scoring'

export default function ScanSummaryBar() {
  const scan = MOCK_SCAN_DETAIL
  const cs = scan.compliance_summary

  return (
    <div className="glass-1 p-4 flex items-center gap-6 flex-wrap">
      {/* Score + Risk Label */}
      <div className="flex items-center gap-3">
        <div className={`text-3xl font-bold ${getScoreColor(scan.vibe_risk_score)}`}>
          {scan.vibe_risk_score}
        </div>
        <div>
          <div className={`text-sm font-semibold ${getScoreColor(scan.vibe_risk_score)}`}>
            {getRiskLabel(scan.vibe_risk_score)}
          </div>
          <div className="text-xs text-textMuted">Vibe Debt Score</div>
        </div>
      </div>

      <div className="w-px h-8 bg-border"></div>

      {/* Findings breakdown */}
      <div className="flex gap-4 text-xs">
        <div className="text-center">
          <div className="text-red font-semibold text-lg">
            {scan.findings.filter(f => f.severity === 'CRITICAL').length}
          </div>
          <div className="text-textMuted">Critical</div>
        </div>
        <div className="text-center">
          <div className="text-amber font-semibold text-lg">
            {scan.findings.filter(f => f.severity === 'HIGH').length}
          </div>
          <div className="text-textMuted">High</div>
        </div>
        <div className="text-center">
          <div className="text-blue font-semibold text-lg">
            {scan.findings.filter(f => f.severity === 'MEDIUM').length}
          </div>
          <div className="text-textMuted">Medium</div>
        </div>
        <div className="text-center">
          <div className="text-textMuted font-semibold text-lg">
            {scan.findings.filter(f => f.severity === 'LOW').length}
          </div>
          <div className="text-textMuted">Low</div>
        </div>
      </div>

      <div className="w-px h-8 bg-border"></div>

      {/* Compliance */}
      <div className="flex gap-3 text-xs">
        <div className="bg-redDim text-red px-2.5 py-1 rounded-lg">
          OWASP: {cs.owasp_violations.length}
        </div>
        <div className="bg-amberDim text-amber px-2.5 py-1 rounded-lg">
          SOC2: {cs.soc2_violations.length}
        </div>
        <div className="bg-blue/10 text-blue px-2.5 py-1 rounded-lg">
          CIS: {cs.cis_violations.length}
        </div>
        <div className={`px-2.5 py-1 rounded-lg ${cs.audit_ready ? 'bg-greenDim text-green' : 'bg-redDim text-red'}`}>
          {cs.audit_ready ? '✓ Audit Ready' : '✕ Not Audit Ready'}
        </div>
      </div>

      <div className="w-px h-8 bg-border"></div>

      {/* Cost */}
      <div className="flex items-center gap-2 text-xs">
        <span className="text-textMuted">Cost:</span>
        <span className="text-green font-medium">${scan.bedrock_cost_usd.toFixed(4)}</span>
        <span className="text-textDim">saved {scan.cost_savings_pct}%</span>
      </div>
    </div>
  )
}
