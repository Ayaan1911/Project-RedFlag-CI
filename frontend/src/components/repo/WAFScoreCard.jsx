import { MOCK_WAF_SCORES } from '../../api/repoMockData'

export default function WAFScoreCard() {
  const data = MOCK_WAF_SCORES;
  
  const getPillarColor = (score) => {
    if (score >= 80) return '#00D084';
    if (score >= 50) return '#FF9F43';
    return '#FF5252';
  };
  
  // Donut chart calculations
  const circumference = 2 * Math.PI * 28; // radius 28
  const strokeDashoffset = circumference - (data.overall / 100) * circumference;

  return (
    <div className="glass-1 flex flex-col pt-[24px] px-[26px] pb-6 h-full">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>WAF Security Posture</h2>
          <p style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '2px' }}>Web Application Firewall alignment</p>
        </div>
        
        {/* SVG Donut */}
        <div className="relative" style={{ width: '64px', height: '64px' }}>
          <svg width="64" height="64" viewBox="0 0 64 64" className="-rotate-90">
            <circle cx="32" cy="32" r="28" stroke="rgba(255,255,255,0.08)" strokeWidth="6" fill="none" />
            <circle cx="32" cy="32" r="28" stroke={getPillarColor(data.overall)} strokeWidth="6" fill="none" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} style={{ transition: 'stroke-dashoffset 1.5s ease-out' }} />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span style={{ font: '700 18px var(--font-display)', color: '#F0F2FF' }}>{data.overall}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col flex-1 justify-between">
        {data.categories.map((c, i) => {
          const color = getPillarColor(c.score);
          const iconColor = c.name === 'Input Validation' || c.name === 'Logging & Monitoring' ? '#6B8EFF' :
                            c.name === 'Data Protection' ? '#9B6DFF' :
                            c.name === 'Rate Limiting' ? '#FF9F43' : '#00D084'; // 'Authentication' and 'Error Handling'
                            
          return (
            <div key={c.name} className="flex items-center gap-[10px]" style={{ '--i': i }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '8px', background: 'rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px', border: '1px solid rgba(255,255,255,0.08)' }}>
                {c.icon}
              </div>
              <span className="flex-1 whitespace-nowrap overflow-hidden text-ellipsis" style={{ font: '500 13px var(--font-body)', color: '#F0F2FF' }}>
                {c.name}
              </span>
              
              {/* Progress bar */}
              <div className="flex-[2] flex items-center gap-[10px] min-w-0">
                <div style={{ flexGrow: 1, minWidth: '0', height: '7px', background: 'rgba(255,255,255,0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div className="waf-bar-fill h-full" style={{ background: color, width: `${c.score}%`, borderRadius: '999px', boxShadow: `0 0 10px ${color}80` }} />
                </div>
                
                {/* Optional issues badge */}
                {c.violations > 0 && (
                  <span style={{ background: 'rgba(255,82,82,0.18)', border: '1px solid rgba(255,82,82,0.32)', borderRadius: '6px', padding: '2px 8px', font: '600 11px var(--font-display)', color: '#FF5252', whiteSpace: 'nowrap' }}>
                    {c.violations}↑
                  </span>
                )}
                
                <span className="text-right" style={{ width: '32px', font: '400 12px var(--font-mono)', color: '#9AA0BC' }}>
                  {c.score}%
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
