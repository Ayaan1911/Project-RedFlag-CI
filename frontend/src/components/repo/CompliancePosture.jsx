import { useState } from 'react';
import { MOCK_COMPLIANCE_POSTURE } from '../../api/repoMockData';

export default function CompliancePosture() {
  const data = MOCK_COMPLIANCE_POSTURE;
  const tabs = data.frameworks.slice(0, 3); // OWASP, SOC2, CIS
  const [activeTab, setActiveTab] = useState(tabs[0].name);

  const activeData = tabs.find(t => t.name === activeTab);

  // Mock detailed rows based on spec
  const getRows = (frameworkName) => {
    if (frameworkName.includes('OWASP')) {
      return [
        { id: 'A03:2021', desc: 'Injection', passed: 7, total: 10 },
        { id: 'A06:2021', desc: 'Vulnerable Components', passed: 9, total: 10 },
        { id: 'A07:2021', desc: 'Auth Failures', passed: 5, total: 10 }
      ];
    }
    if (frameworkName.includes('SOC')) {
      return [
        { id: 'CC6.1', desc: 'Logical Access Controls', passed: 18, total: 20 },
        { id: 'CC6.6', desc: 'Transmission Integrity', passed: 14, total: 15 },
        { id: 'CC6.7', desc: 'Data Retention', passed: 8, total: 8 },
        { id: 'CC8.1', desc: 'Change Management', passed: 2, total: 10 }
      ];
    }
    return [
      { id: 'CIS 2.1', desc: 'Software Inventory', passed: 4, total: 5 },
      { id: 'CIS 5.1', desc: 'IAM Hardening', passed: 8, total: 10 },
      { id: 'CIS 13.1', desc: 'Data Protection', passed: 3, total: 10 }
    ];
  };

  const rows = getRows(activeTab);

  const getColor = (pct) => {
    if (pct >= 80) return '#00D084';
    if (pct >= 50) return '#FF9F43';
    return '#FF5252';
  };

  const totalViolations = 12;

  return (
    <div className="glass-1" style={{ padding: '24px 28px', width: '100%' }}>
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>Compliance Posture</h2>
        <div style={{ background: 'rgba(255,45,107,0.15)', border: '1px solid rgba(255,45,107,0.30)', color: '#FF2D6B', font: '700 12px var(--font-display)', padding: '4px 12px', borderRadius: '999px' }}>
          [{totalViolations} total violations]
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-[var(--divider)] pb-1">
        {tabs.map(t => {
          const isActive = activeTab === t.name;
          return (
            <button
              key={t.name}
              onClick={() => setActiveTab(t.name)}
              style={isActive ? {
                background: 'rgba(255,255,255,0.08)',
                border: '1px solid rgba(255,255,255,0.12)',
                color: '#F0F2FF',
                borderRadius: '8px 8px 0 0',
                borderBottom: '2px solid #4A6CF7',
                padding: '8px 16px',
                font: '500 13px var(--font-body)',
                cursor: 'pointer'
              } : {
                color: '#4A5070',
                padding: '8px 16px',
                font: '500 13px var(--font-body)',
                borderBottom: '2px solid transparent',
                cursor: 'pointer'
              }}
              className="transition-colors hover:text-[#F0F2FF]"
            >
              {t.name}
            </button>
          )
        })}
      </div>

      {/* Rows */}
      <div className="flex flex-col gap-2 mb-6">
        {rows.map((r, i) => {
          const pct = Math.round((r.passed / r.total) * 100);
          const color = getColor(pct);

          return (
            <div key={r.id} className="flex items-center hover:bg-[rgba(255,255,255,0.025)] p-2 rounded-lg transition-colors group" style={{ '--i': i }}>
              <span style={{ font: '600 14px var(--font-mono)', color: '#6B8EFF', minWidth: '110px' }}>
                {r.id} <span style={{ color: '#4A5070', fontWeight: 400 }}>—</span>
              </span>
              <span className="flex-1" style={{ font: '400 13px var(--font-body)', color: '#F0F2FF' }}>
                {r.desc}
              </span>
              <div className="flex items-center gap-4 hidden sm:flex">
                <span style={{ font: '400 12px var(--font-body)', color: '#9AA0BC' }}>
                  {r.passed}/{r.total} passing
                </span>
                <span style={{ font: '400 12px var(--font-mono)', color: color, width: '32px', textAlign: 'right' }}>
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

      {/* Violated Pills at Bottom */}
      <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
        {activeData.violations.map(v => {
          // parse prefix ID if format is "ID — Description"
          const vLabel = v.includes('—') ? v.split('—')[0].trim() : v;
          return (
            <div key={v} style={{ background: 'rgba(255,45,107,0.12)', border: '1px solid rgba(255,45,107,0.25)', borderRadius: '999px', padding: '4px 12px', font: '600 11px var(--font-mono)', color: '#FF2D6B', whiteSpace: 'nowrap' }}>
              {vLabel}
            </div>
          )
        })}
      </div>
    </div>
  )
}
