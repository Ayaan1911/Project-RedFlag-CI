import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function FindingExpandable({ findings }) {
  const [expandedId, setExpandedId] = useState(null);
  const { repoId = 'demo', prNumber } = useParams();
  const navigate = useNavigate();

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getSeverityStyles = (severity) => {
    switch(severity) {
      case 'CRITICAL': return { bg: 'rgba(255,82,82,0.20)', border: 'rgba(255,82,82,0.40)', color: '#FF5252' };
      case 'HIGH': return { bg: 'rgba(255,159,67,0.18)', border: 'rgba(255,159,67,0.30)', color: '#FF9F43' };
      case 'MEDIUM': return { bg: 'rgba(74,108,247,0.18)', border: 'rgba(74,108,247,0.28)', color: '#6B8EFF' };
      default: return { bg: 'rgba(155,109,255,0.15)', border: 'rgba(155,109,255,0.25)', color: '#9B6DFF' };
    }
  };

  return (
    <div className="glass-1 w-full flex flex-col pt-6 pb-2">
      {/* Search Header */}
      <div className="flex justify-between items-center mb-6 px-[26px]">
        <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>Recent Findings</h2>
        <div className="flex gap-3">
          <div className="glass-btn-outline cursor-pointer" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '6px 12px', font: '500 12px var(--font-body)', color: '#9AA0BC' }}>Filter: All ▾</div>
          <div className="glass-btn-outline cursor-pointer" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '6px 12px', font: '500 12px var(--font-body)', color: '#9AA0BC' }}>Severity: All ▾</div>
          <div className="glass-btn-outline cursor-pointer" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '6px 12px', font: '500 12px var(--font-body)', color: '#F0F2FF' }}>PR: #42 ▾</div>
        </div>
      </div>

      <div className="flex flex-col w-full">
        {findings.map(f => {
          const isExpanded = expandedId === f.id;
          const sevStyle = getSeverityStyles(f.severity);

          return (
            <div key={f.id} className="w-full relative" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              {/* Row */}
              <div 
                className="flex items-center px-[26px] cursor-pointer hover:bg-[rgba(255,255,255,0.025)] transition-colors h-[56px]"
                onClick={() => toggleExpand(f.id)}
              >
                <div style={{ width: '24px', color: '#9AA0BC', transition: 'transform 0.2s', transform: isExpanded ? 'rotate(90deg)' : 'rotate(0)' }}>
                  ▸
                </div>
                
                <div style={{ background: sevStyle.bg, border: `1px solid ${sevStyle.border}`, borderRadius: '6px', padding: '2px 8px', color: sevStyle.color, font: '700 11px var(--font-display)', minWidth: '76px', textAlign: 'center' }}>
                  {f.severity}
                </div>
                
                <div style={{ font: '600 14px var(--font-display)', color: '#F0F2FF', marginLeft: '16px', minWidth: '180px' }}>
                  {f.type}
                </div>
                
                <div style={{ font: '400 12px var(--font-mono)', color: '#6B8EFF', marginLeft: '12px' }}>
                  {f.file}:{f.line}
                </div>

                <div className="flex-1 flex justify-end gap-2 pr-2">
                  {f.complianceViolations.map(cv => (
                    <div key={cv} style={{ background: 'rgba(74,108,247,0.12)', border: '1px solid rgba(74,108,247,0.22)', borderRadius: '999px', padding: '3px 10px', font: '600 10px var(--font-mono)', color: '#6B8EFF' }}>
                      {cv}
                    </div>
                  ))}
                </div>
              </div>

              {/* Expanded Panel */}
              {isExpanded && (
                <div className="finding-panel bg-[rgba(0,0,0,0.2)] pb-[20px]" style={{ paddingLeft: '48px', paddingRight: '26px' }}>
                  <p style={{ font: '400 13px var(--font-body)', color: '#9AA0BC', marginBottom: '20px', paddingTop: '10px' }}>
                    {f.description}
                  </p>

                  <div className="flex flex-col lg:flex-row gap-5 mb-5">
                    {/* Exploit Payload */}
                    {f.exploitPayload && (
                      <div className="flex-1 rounded-xl p-4" style={{ background: 'rgba(255,82,82,0.06)', border: '1px solid rgba(255,82,82,0.18)' }}>
                        <div style={{ font: '600 13px var(--font-display)', color: '#FF5252', marginBottom: '12px' }}>
                          🔴 Exploit Payload
                        </div>
                        <pre style={{ font: '400 12px var(--font-mono)', color: '#FF8888', whiteSpace: 'pre-wrap', background: 'rgba(0,0,0,0.3)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,82,82,0.1)' }}>
                          {f.exploitPayload}
                        </pre>
                      </div>
                    )}

                    {/* Root Cause */}
                    {f.rootCause && (
                      <div className="flex-1 rounded-xl p-4" style={{ background: 'rgba(255,159,67,0.06)', border: '1px solid rgba(255,159,67,0.16)' }}>
                        <div style={{ font: '600 13px var(--font-display)', color: '#FF9F43', marginBottom: '12px' }}>
                          💡 Root Cause
                        </div>
                        <div style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,159,67,0.1)', borderRadius: '8px', padding: '12px' }}>
                          <div style={{ font: '600 12px var(--font-mono)', color: '#FF9F43', marginBottom: '6px' }}>[{f.rootCause.pattern}]</div>
                          <p style={{ font: '400 12px var(--font-body)', color: '#9AA0BC' }}>{f.rootCause.description}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Fix Code */}
                  {f.fixCode && (
                    <div className="w-full rounded-xl p-4 mb-5 relative" style={{ background: 'rgba(0,208,132,0.05)', border: '1px solid rgba(0,208,132,0.14)' }}>
                      <div className="flex justify-between items-center mb-3">
                        <div style={{ font: '600 13px var(--font-display)', color: '#00D084' }}>
                          ✅ Auto-Generated Fix
                        </div>
                        <div className="flex gap-2">
                          <button 
                            onClick={() => navigate(`/diff/${repoId}/${prNumber || f.prNumber || '0'}/${findings.findIndex(item => item.id === f.id)}`)}
                            style={{ background: 'transparent', border: '1px solid #E63946', color: '#E63946', borderRadius: '6px', padding: '4px 10px', font: '600 11px var(--font-body)', cursor: 'pointer' }} className="hover:bg-red/10 transition-colors"
                          >
                            View Diff →
                          </button>
                          <button style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '6px', padding: '4px 10px', font: '500 11px var(--font-body)', color: '#F0F2FF', cursor: 'pointer' }} className="hover:bg-[rgba(255,255,255,0.15)] transition-colors">Copy</button>
                          <button style={{ background: 'rgba(0,208,132,0.20)', border: '1px solid rgba(0,208,132,0.40)', borderRadius: '6px', padding: '4px 10px', font: '600 11px var(--font-body)', color: '#00D084', cursor: 'pointer' }} className="hover:bg-[rgba(0,208,132,0.30)] transition-colors">Apply Fix →</button>
                        </div>
                      </div>
                      
                      <div style={{ background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '14px', fontFamily: 'var(--font-mono)', color: '#E2E8F0', fontSize: '13px', overflowX: 'auto' }}>
                        <pre style={{ margin: 0 }}>
                          {f.fixCode.split('\n').map((line, idx) => {
                            const isPurple = line.includes('const ') || line.includes('if ') || line.includes('import ');
                            const isGreen = line.includes("'") || line.includes('"');
                            return (
                                <div key={idx} className="flex">
                                  <span style={{ width: '24px', color: '#4A5070', userSelect: 'none' }}>{idx + 1}</span>
                                  <span style={{ color: isPurple ? '#9B6DFF' : isGreen ? '#00D084' : '#6B8EFF' }}>
                                    {line}
                                  </span>
                                </div>
                            )
                          })}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Audit Impact Badge */}
                  {f.auditImpact && (
                    <div className="flex items-center gap-2 w-fit" style={{ background: 'rgba(255,159,67,0.08)', borderRadius: '8px', padding: '8px 14px', border: '1px solid rgba(255,159,67,0.2)' }}>
                      <span>⚠️</span>
                      <span style={{ font: '500 13px var(--font-body)', color: '#FF9F43' }}>{f.auditImpact}</span>
                    </div>
                  )}

                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
