import { MOCK_FINOPS } from '../../api/repoMockData'

export default function RouterSavingsCard() {
  const { totalCost, totalWithoutRouting, savingsPercent, modelBreakdown } = MOCK_FINOPS
  const haikuRouted = modelBreakdown[0].calls
  const sonnetRouted = modelBreakdown[1].calls
  const totalRequests = haikuRouted + sonnetRouted
  const costSavedPercent = savingsPercent
  const estimatedSavings = (totalWithoutRouting - totalCost).toFixed(2)

  return (
    <div className="glass-blue cost-card flex flex-col justify-between h-full group overflow-hidden">
      {/* Header and Smart Router Badge */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-section-title text-textPrimary">Bedrock Routing</h3>
        <span className="smart-router-pill">
          ✦ Smart Router
        </span>
      </div>

      {/* Main Stat Area */}
      <div className="flex flex-col gap-1 mb-6 mt-auto">
        <div className="font-mono text-[11px] text-textSecondary uppercase tracking-widest mb-1 opacity-80">Cost Avoided</div>
        <div className="flex items-end gap-3">
          <span className="cost-actual">${estimatedSavings}</span>
          <span className="cost-original">${totalWithoutRouting.toFixed(2)}</span>
        </div>
      </div>

      {/* Savings Progress Bar */}
      <div className="mb-8 relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-label">Optimization</span>
          <span className="font-display font-bold text-[14px] text-brandGreen">{costSavedPercent}%</span>
        </div>
        <div className="savings-bar-track w-full">
          <div 
            className="savings-bar-fill top-0 left-0 absolute"
            style={{ width: `${costSavedPercent}%` }}
          />
        </div>
      </div>

      {/* Sub-cards (Haiku / Sonnet Pills) via Stacked Liquid Glass */}
      <div className="flex gap-2 relative z-10">
        <div className="glass-subcard flex-1 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-brandBlueLight shadow-[0_0_8px_var(--blue-glow)]" />
            <span className="text-label !text-[#111118]">Haiku</span>
          </div>
          <span className="font-display font-semibold text-[13px]">{Math.round((haikuRouted / totalRequests) * 100)}%</span>
        </div>
        
        <div className="glass-subcard flex-1 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-brandPurple shadow-[0_0_8px_var(--purple-glow)]" />
            <span className="text-label !text-[#111118]">Sonnet</span>
          </div>
          <span className="font-display font-semibold text-[13px]">{Math.round((sonnetRouted / totalRequests) * 100)}%</span>
        </div>
      </div>
    </div>
  )
}
