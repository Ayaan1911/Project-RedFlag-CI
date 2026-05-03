import { useNavigate } from 'react-router-dom'

export default function RepoBanner({ repo }) {
  const navigate = useNavigate()

  const getDebtColor = (score) => {
    if (score > 70) return '#FF5252'
    if (score >= 50) return '#FF9F43'
    return '#00D084'
  }

  const repoData = repo || {
    name: 'Unknown repository',
    description: 'No repository data available',
    language: 'Unknown',
    lastScan: null,
    techDebtScore: 0,
    vibeCodeRatio: 0,
    totalScans: 0,
    repoUrl: null,
  }

  return (
    <div className="glass-2 relative flex items-center justify-between" style={{ padding: '28px 36px', background: 'rgba(255,255,255,0.065)', borderTopColor: 'rgba(255,255,255,0.18)' }}>
      <div className="absolute top-6 right-8 flex items-center gap-3">
        <button onClick={() => navigate('/')} className="text-[13px] font-body text-[var(--text-secondary)] hover:text-white transition-colors cursor-pointer mr-2">
          ← Back
        </button>
        <button
          className="hover:bg-[rgba(255,255,255,0.1)] cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', borderRadius: '999px', padding: '8px 18px', font: '600 13px var(--font-display)', color: '#F0F2FF', transition: 'all 0.2s' }}
          onClick={() => repoData.repoUrl && window.open(repoData.repoUrl, '_blank')}
          disabled={!repoData.repoUrl}
        >
          View on GitHub ↗
        </button>
      </div>

      <div className="flex gap-5 items-center mt-2">
        <div style={{ width: '40px', height: '40px', background: 'rgba(255,159,67,0.15)', border: '1px solid rgba(255,159,67,0.28)', borderRadius: '12px' }} className="flex items-center justify-center text-[18px]">
          📁
        </div>

        <div className="flex flex-col">
          <h1 style={{ font: '700 26px var(--font-display)', letterSpacing: '-0.8px', color: '#F0F2FF' }}>{repoData.name}</h1>
          <p style={{ font: '400 13px var(--font-body)', color: '#4A5070', marginTop: '2px', marginBottom: '8px' }}>
            {repoData.description}
          </p>
          <div className="flex items-center gap-2">
            <span style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.11)', borderRadius: '999px', padding: '4px 12px', font: '500 11px var(--font-body)' }}>
              {repoData.language}
            </span>
            <span style={{ background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.11)', borderRadius: '999px', padding: '4px 12px', font: '500 11px var(--font-body)' }}>
              Last scan {repoData.lastScan ? new Date(repoData.lastScan).toLocaleString() : 'unknown'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center mt-8 pr-4">
        <div className="flex flex-col items-center px-8">
          <span style={{ font: '700 42px var(--font-display)', color: getDebtColor(repoData.techDebtScore), lineHeight: '1' }}>{repoData.techDebtScore}</span>
          <span style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '6px' }}>Vibe Debt</span>
        </div>
        <div style={{ width: '1px', height: '36px', background: 'rgba(255,255,255,0.07)' }}></div>
        <div className="flex flex-col items-center px-8">
          <span style={{ font: '700 42px var(--font-display)', color: '#9B6DFF', lineHeight: '1' }}>{repoData.vibeCodeRatio}%</span>
          <span style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '6px' }}>AI-Generated</span>
        </div>
        <div style={{ width: '1px', height: '36px', background: 'rgba(255,255,255,0.07)' }}></div>
        <div className="flex flex-col items-center px-8">
          <span style={{ font: '700 42px var(--font-display)', color: '#6B8EFF', lineHeight: '1' }}>{repoData.totalScans}</span>
          <span style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '6px' }}>Total Scans</span>
        </div>
      </div>
    </div>
  )
}
