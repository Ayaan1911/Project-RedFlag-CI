import { MOCK_COMPLIANCE_POSTURE } from '../../api/repoMockData'

export default function CompliancePosture() {
  const { frameworks } = MOCK_COMPLIANCE_POSTURE

  return (
    <div className="glass-1 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-text">Compliance Posture</h3>
        <span className="text-xs text-red bg-redDim px-2 py-0.5 rounded-full">
          {frameworks.reduce((s, f) => s + f.violated, 0)} total violations
        </span>
      </div>

      <div className="space-y-4">
        {frameworks.map((fw) => {
          const passRate = Math.round(((fw.totalControls - fw.violated) / fw.totalControls) * 100)
          const barColor = passRate >= 90 ? 'bg-green' : passRate >= 70 ? 'bg-amber' : 'bg-red'

          return (
            <div key={fw.name} className="bg-bg rounded-lg border border-border p-4">
              {/* Framework header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{fw.icon}</span>
                  <span className="text-sm font-medium text-text">{fw.name}</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-textMuted">{fw.totalControls - fw.violated}/{fw.totalControls} passing</span>
                  <span className={`font-medium ${passRate >= 90 ? 'text-green' : passRate >= 70 ? 'text-amber' : 'text-red'}`}>
                    {passRate}%
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="h-1.5 bg-surfaceAlt rounded-full overflow-hidden mb-3">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${barColor}`}
                  style={{ width: `${passRate}%` }}
                ></div>
              </div>

              {/* Violations */}
              {fw.violated > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {fw.violations.map((v, i) => (
                    <span key={i} className="text-[11px] bg-surfaceAlt text-textMuted px-2 py-0.5 rounded border border-border">
                      {v}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
