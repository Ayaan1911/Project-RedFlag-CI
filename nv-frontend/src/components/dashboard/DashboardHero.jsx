import { MOCK_METRICS } from '../../api/mockData'
import { useCountUp } from '../../hooks/useAnimations'

function LargeStatCounter({ value, label, trend, isPercent = false, trendDir = 'up', type = 'critical' }) {
  const numValue = isPercent ? parseInt(value) : value
  const { count, ref } = useCountUp(numValue, 1400)

  // Use exact CSS from prompt
  const trendClass = trendDir === 'up' ? 'stat-trend up' : 'stat-trend down'
  const trendIcon = trendDir === 'up' ? '↗' : '↘'
  const numClass = `stat-number ${type}`

  return (
    <div ref={ref} className="flex flex-col items-center">
      <div className="flex gap-2 items-start h-[24px]">
        {trend && (
          <span className={trendClass}>
            {trendIcon} {trend}%
          </span>
        )}
      </div>
      <div className={numClass}>
        {isPercent ? `${count}%` : count}
      </div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

function ProgressBar({ label, percentage, type }) {
  // Map prompt styles
  let fillClass = ''
  switch (type) {
    case 'pink': fillClass = 'progress-fill-pink'; break;
    case 'white': fillClass = 'progress-fill-white'; break;
    case 'blue': fillClass = 'progress-fill-blue'; break;
    case 'hatched': fillClass = 'progress-fill-stripe'; break;
  }

  return (
    <div className="w-[110px] sm:w-[130px]">
      <div className="text-label mb-[6px]">{label}</div>
      <div className="progress-track">
        <div 
          className={`absolute left-0 top-0 h-full ${fillClass}`}
          style={{ width: type === 'dark' || type === 'hatched' ? '40%' : percentage }}
        />
      </div>
    </div>
  )
}

export default function DashboardHero() {
  return (
    <div className="glass-2 hero-card flex flex-col w-full">
      {/* Top Section */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="hero-title text-page-title">
            Security Dashboard
          </h1>
          <p className="hero-subtitle">
            RedFlag CI • acme/vibe-app
          </p>
        </div>
        
        <div className="flex gap-3 pt-2">
          <span className="hero-pill flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--pink)] shadow-[0_0_8px_var(--pink-glow)]" />
            7 Problem Statements
          </span>
          <span className="hero-pill flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--blue-light)] shadow-[0_0_8px_var(--blue-glow)]" />
            1 Pipeline
          </span>
        </div>
      </div>

      {/* Bottom Section (Progress bars + Big counters) */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mt-4">
        
        {/* Progress Bars */}
        <div className="flex flex-wrap gap-[24px]">
          <ProgressBar label="Tech Debt Risk" percentage="20%" type="pink" />
          <ProgressBar label="AI Generated" percentage="25%" type="white" />
          <ProgressBar label="Code Covered" percentage="40%" type="blue" />
          <ProgressBar label="Fail Rate" percentage="15%" type="hatched" />
        </div>

        {/* Big Resq.io Stats Right-aligned */}
        <div className="flex items-end gap-10 lg:gap-[60px]">
          <LargeStatCounter 
            value={MOCK_METRICS.criticalFindings} 
            label="Critical issues" 
            trend={12} 
            trendDir="down"
            type="critical"
          />
          <LargeStatCounter 
            value={MOCK_METRICS.secretsBlocked} 
            label="Secrets blocked" 
            trend={24}
            trendDir="up" 
            type="secrets"
          />
          <LargeStatCounter 
            value={MOCK_METRICS.costSavings} 
            label="Cost savings" 
            trend={-14} 
            trendDir="up"
            isPercent={true} 
            type="savings"
          />
        </div>
      </div>
    </div>
  )
}
