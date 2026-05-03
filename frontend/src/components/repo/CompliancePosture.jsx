import { useState } from 'react'

export default function CompliancePosture({ data }) {
  const frameworks = buildFrameworks(data)
  const tabs = frameworks.slice(0, 3)
  const [activeTab, setActiveTab] = useState(tabs[0]?.name || '')

  const activeData = tabs.find((tab) => tab.name === activeTab) || tabs[0] || { name: '', violations: [] }
  const rows = activeData.violations.map((violation) => ({ id: violation, desc: violation, passed: 0, total: 1 }))

  const getColor = (pct) => {
    if (pct >= 80) return '#00D084'
    if (pct >= 50) return '#FF9F43'
    return '#FF5252'
  }

  const totalViolations = frameworks.reduce((sum, framework) => sum + framework.violations.length, 0)

  return (
    <div className="glass-1" style={{ padding: '24px 28px', width: '100%' }}>
      <div className="flex justify-between items-center mb-4">
        <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>Compliance Posture</h2>
        <div style={{ background: 'rgba(255,45,107,0.15)', border: '1px solid rgba(255,45,107,0.30)', color: '#FF2D6B', font: '700 12px var(--font-display)', padding: '4px 12px', borderRadius: '999px' }}>
          [{totalViolations} total violations]
        </div>
      </div>

      <div className="flex gap-2 mb-6 border-b border-[var(--divider)] pb-1">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.name
          return (
            <button
              key={tab.name}
              onClick={() => setActiveTab(tab.name)}
              style={isActive ? {
                background: 'rgba(255,255,255,0.08)',
                border: '1px solid rgba(255,255,255,0.12)',
                color: '#F0F2FF',
                borderRadius: '8px 8px 0 0',
                borderBottom: '2px solid #4A6CF7',
                padding: '8px 16px',
                font: '500 13px var(--font-body)',
                cursor: 'pointer',
              } : {
                color: '#4A5070',
                padding: '8px 16px',
                font: '500 13px var(--font-body)',
                borderBottom: '2px solid transparent',
                cursor: 'pointer',
              }}
              className="transition-colors hover:text-[#F0F2FF]"
            >
              {tab.name}
            </button>
          )
        })}
      </div>

      <div className="flex flex-col gap-2 mb-6">
        {rows.map((row, i) => {
          const pct = Math.round((row.passed / row.total) * 100)
          const color = getColor(pct)

          return (
            <div key={row.id} className="flex items-center hover:bg-[rgba(255,255,255,0.025)] p-2 rounded-lg transition-colors group" style={{ '--i': i }}>
              <span style={{ font: '600 14px var(--font-mono)', color: '#6B8EFF', minWidth: '110px' }}>
                {row.id} <span style={{ color: '#4A5070', fontWeight: 400 }}>-</span>
              </span>
              <span className="flex-1" style={{ font: '400 13px var(--font-body)', color: '#F0F2FF' }}>
                {row.desc}
              </span>
              <div className="flex items-center gap-4 hidden sm:flex">
                <span style={{ font: '400 12px var(--font-body)', color: '#9AA0BC' }}>
                  {row.passed}/{row.total} passing
                </span>
                <span style={{ font: '400 12px var(--font-mono)', color, width: '32px', textAlign: 'right' }}>
                  {pct}%
                </span>
                <div style={{ width: '120px', height: '6px', background: 'rgba(255,255,255,0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div className="compliance-bar-fill h-full" style={{ width: `${pct}%`, background: color, borderRadius: '999px', boxShadow: `0 0 10px ${color}80` }} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
        {activeData.violations.map((violation) => (
          <div key={violation} style={{ background: 'rgba(255,45,107,0.12)', border: '1px solid rgba(255,45,107,0.25)', borderRadius: '999px', padding: '4px 12px', font: '600 11px var(--font-mono)', color: '#FF2D6B', whiteSpace: 'nowrap' }}>
            {violation}
          </div>
        ))}
      </div>
    </div>
  )
}

function buildFrameworks(summary) {
  return [
    { name: 'OWASP Top 10', violations: summary?.owasp_violations || [] },
    { name: 'SOC 2 Type II', violations: summary?.soc2_violations || [] },
    { name: 'CIS Benchmarks', violations: summary?.cis_violations || [] },
  ]
}
