import { useNavigate, useParams } from 'react-router-dom'

export default function RepoScanHistoryTable({ scans = [] }) {
  const navigate = useNavigate()
  const { repoId } = useParams()

  const getScoreColor = (score) => {
    if (score >= 80) return '#FF5252'
    if (score >= 50) return '#FF9F43'
    return '#00D084'
  }

  return (
    <div className="glass-1 flex flex-col pt-6 pb-2 px-6 h-full">
      <div className="flex justify-between items-center mb-6">
        <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>Scan History</h2>
        <div style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', padding: '6px 12px', font: '500 12px var(--font-body)', color: '#9AA0BC', cursor: 'pointer' }}>
          Filter: All ▼
        </div>
      </div>

      <div className="w-full overflow-x-auto custom-scrollbar flex-1">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr>
              {['PR', 'Vibe Score', 'AI Conf', 'Critical', 'High', 'Medium', 'Time'].map((header) => (
                <th key={header} style={{ font: '500 11px var(--font-mono)', textTransform: 'uppercase', letterSpacing: '1px', color: '#4A5070', paddingBottom: '16px', fontWeight: 'normal' }}>
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {scans.map((row, i) => {
              const active = i === 0
              const vibeScore = row?.vibeScore ?? 0
              const aiConf = row?.aiConf
              const critical = row?.critical
              const high = row?.high
              const medium = row?.medium
              const sColor = getScoreColor(vibeScore)
              const prNum = String(row?.prNumber ?? '')
              const currentRepo = row?.repoId || repoId || 'unknown'

              return (
                <tr
                  key={`${currentRepo}-${row?.prNumber ?? i}`}
                  className="table-body-row group"
                  onClick={() => navigate(`/scan/${currentRepo}/${prNum}`)}
                  style={active ? {
                    background: 'rgba(255,45,107,0.05)',
                    boxShadow: 'inset 3px 0 0 #FF2D6B',
                    cursor: 'pointer',
                  } : { cursor: 'pointer' }}
                >
                  <td style={{ padding: '12px 0 12px 12px' }}>
                    <span className="group-hover:underline" style={{ font: '600 13px var(--font-mono)', color: '#6B8EFF' }}>
                      {row?.prNumber != null ? `#${row.prNumber}` : '-'}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <div className="flex flex-col gap-[6px]">
                      <div>
                        <span style={{ font: '700 14px var(--font-display)', color: sColor }}>{vibeScore}</span>
                        <span style={{ font: '400 12px var(--font-body)', color: '#4A5070' }}>/100</span>
                      </div>
                      <div style={{ width: '60px', height: '4px', background: 'rgba(255,255,255,0.05)', borderRadius: '999px', overflow: 'hidden' }}>
                        <div style={{ width: `${vibeScore}%`, height: '100%', background: sColor }} />
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 8px', font: '400 13px var(--font-mono)', color: '#9B6DFF' }}>
                    {aiConf != null ? `${aiConf}%` : '-'}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    {critical > 0 ? (
                      <div className="flex items-center justify-center" style={{ width: '26px', height: '26px', background: 'rgba(255,82,82,0.18)', border: '1px solid rgba(255,82,82,0.32)', borderRadius: '6px', color: '#FF5252', font: '700 12px var(--font-display)' }}>
                        {critical}
                      </div>
                    ) : <span style={{ color: '#4A5070', marginLeft: '8px' }}>-</span>}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    {high > 0 ? (
                      <div className="flex items-center justify-center" style={{ width: '26px', height: '26px', background: 'rgba(255,159,67,0.18)', border: '1px solid rgba(255,159,67,0.30)', borderRadius: '6px', color: '#FF9F43', font: '700 12px var(--font-display)' }}>
                        {high}
                      </div>
                    ) : <span style={{ color: '#4A5070', marginLeft: '8px' }}>-</span>}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    {medium > 0 ? (
                      <div className="flex items-center justify-center" style={{ width: '26px', height: '26px', background: 'rgba(74,108,247,0.18)', border: '1px solid rgba(74,108,247,0.28)', borderRadius: '6px', color: '#6B8EFF', font: '700 12px var(--font-display)' }}>
                        {medium}
                      </div>
                    ) : <span style={{ color: '#4A5070', marginLeft: '8px' }}>-</span>}
                  </td>
                  <td style={{ padding: '12px 8px', font: '400 11px var(--font-mono)', color: '#4A5070', whiteSpace: 'nowrap' }}>
                    {row?.time ? row.time.split('T')[0] : '-'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="flex justify-between items-center mt-3 pt-4 border-t border-[rgba(255,255,255,0.05)]">
        <span style={{ font: '400 11px var(--font-body)', color: '#4A5070' }}>Showing 1-{scans.length} of {scans.length} scans</span>
        <div className="flex gap-2">
          <button style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '999px', padding: '4px 12px', color: '#9AA0BC', font: '500 12px var(--font-body)', cursor: 'pointer' }} className="hover:bg-[rgba(255,255,255,0.08)] transition-colors">Prev</button>
          <button style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '999px', padding: '4px 12px', color: '#F0F2FF', font: '500 12px var(--font-body)', cursor: 'pointer' }} className="hover:bg-[rgba(255,255,255,0.15)] transition-colors">Next</button>
        </div>
      </div>
    </div>
  )
}
