export default function WAFScoreCard({ data }) {
  const scoreData = data || { overall: 0, categories: [] }
  const iconMap = {
    Shield: '🛡️',
    Lock: '🔐',
    Disk: '💾',
    Timer: '⏱️',
    Scan: '🧯',
    List: '📋',
  }

  const getPillarColor = (score) => {
    if (score >= 80) return '#00D084'
    if (score >= 50) return '#FF9F43'
    return '#FF5252'
  }

  const circumference = 2 * Math.PI * 28
  const strokeDashoffset = circumference - (scoreData.overall / 100) * circumference

  return (
    <div className="glass-1 flex flex-col pt-[24px] px-[26px] pb-6 h-full">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>WAF Security Posture</h2>
          <p style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '2px' }}>Web Application Firewall alignment</p>
        </div>

        <div className="relative" style={{ width: '64px', height: '64px' }}>
          <svg width="64" height="64" viewBox="0 0 64 64" className="-rotate-90">
            <circle cx="32" cy="32" r="28" stroke="rgba(255,255,255,0.08)" strokeWidth="6" fill="none" />
            <circle cx="32" cy="32" r="28" stroke={getPillarColor(scoreData.overall)} strokeWidth="6" fill="none" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} style={{ transition: 'stroke-dashoffset 1.5s ease-out' }} />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span style={{ font: '700 18px var(--font-display)', color: '#F0F2FF' }}>{scoreData.overall}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col flex-1 justify-between">
        {scoreData.categories.map((category, i) => {
          const color = getPillarColor(category.score)
          return (
            <div key={category.name} className="flex items-center gap-[10px]" style={{ '--i': i }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', border: '1px solid rgba(255,255,255,0.08)' }}>
                {iconMap[category.icon] || category.icon}
              </div>
              <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis" style={{ font: '500 13px var(--font-body)', color: '#F0F2FF' }}>
                {category.name}
              </span>

              <div className="flex-[2] flex items-center gap-[10px] min-w-0">
                <div style={{ flexGrow: 1, minWidth: '0', height: '7px', background: 'rgba(255,255,255,0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div className="waf-bar-fill h-full" style={{ background: color, width: `${category.score}%`, borderRadius: '999px', boxShadow: `0 0 10px ${color}80` }} />
                </div>

                {category.violations > 0 && (
                  <span style={{ background: 'rgba(255,82,82,0.18)', border: '1px solid rgba(255,82,82,0.32)', borderRadius: '6px', padding: '2px 8px', font: '600 11px var(--font-display)', color: '#FF5252', whiteSpace: 'nowrap' }}>
                    {category.violations}^
                  </span>
                )}

                <span className="text-right" style={{ width: '32px', font: '400 12px var(--font-mono)', color: '#9AA0BC' }}>
                  {category.score}%
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
