import { MOCK_WAF_SCORES } from '../../api/repoMockData'

export default function WAFScoreCard() {
  const waf = MOCK_WAF_SCORES

  const getBarColor = (score) => {
    if (score >= 80) return 'bg-green'
    if (score >= 50) return 'bg-amber'
    return 'bg-red'
  }

  const getTextColor = (score) => {
    if (score >= 80) return 'text-green'
    if (score >= 50) return 'text-amber'
    return 'text-red'
  }

  return (
    <div className="glass-1 p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-sm font-medium text-text">WAF Security Posture</h3>
          <p className="text-xs text-textMuted mt-0.5">Web Application Firewall alignment</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-14 h-14">
            <svg viewBox="0 0 48 48" className="w-14 h-14 -rotate-90">
              <circle cx="24" cy="24" r="20" fill="none" stroke="#2a2a2a" strokeWidth="3" />
              <circle
                cx="24" cy="24" r="20" fill="none"
                stroke={waf.overall >= 80 ? '#39d353' : waf.overall >= 50 ? '#f0a500' : '#E63946'}
                strokeWidth="3"
                strokeDasharray={`${(waf.overall / 100) * 125.6} 125.6`}
                strokeLinecap="round"
              />
            </svg>
            <span className={`absolute inset-0 flex items-center justify-center text-sm font-bold ${getTextColor(waf.overall)}`}>
              {waf.overall}
            </span>
          </div>
        </div>
      </div>

      {/* Categories */}
      <div className="space-y-3">
        {waf.categories.map((cat) => (
          <div key={cat.name}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2 text-xs">
                <span>{cat.icon}</span>
                <span className="text-text">{cat.name}</span>
              </div>
              <div className="flex items-center gap-2">
                {cat.violations > 0 && (
                  <span className="text-[10px] text-red bg-redDim px-1.5 py-0.5 rounded">
                    {cat.violations} issues
                  </span>
                )}
                <span className={`text-xs font-medium ${getTextColor(cat.score)}`}>
                  {cat.score}%
                </span>
              </div>
            </div>
            <div className="h-1.5 bg-surfaceAlt rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${getBarColor(cat.score)}`}
                style={{ width: `${cat.score}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
