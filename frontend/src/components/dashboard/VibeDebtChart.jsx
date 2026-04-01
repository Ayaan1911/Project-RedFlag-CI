import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts'
import { MOCK_CHART_DATA } from '../../api/mockData'

function CustomTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[rgba(15,15,28,0.90)] backdrop-blur-[16px] border border-[rgba(255,255,255,0.12)] p-3 rounded-[10px]">
        <p className="text-[11px] font-mono text-white font-medium mb-1.5">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <span 
              className="w-2 h-2 rounded-full border border-[rgba(255,255,255,0.5)]" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-[12px] font-sans text-textSecondary">{entry.name}:</span>
            <span className="text-[12px] font-sans text-white font-medium ml-auto">
              {entry.value}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function VibeDebtChart() {
  return (
    <div className="glass-1 chart-card h-full flex flex-col pt-0">
      <div className="flex items-center justify-between mb-4 mt-6">
        <h3 className="text-section-title text-textPrimary">Vibe Debt Trends</h3>
        <div className="flex bg-[rgba(255,255,255,0.06)] rounded-full p-1 border border-[rgba(255,255,255,0.1)]">
          <button className="px-4 py-1 text-[12px] font-medium font-sans text-textSecondary hover:text-white transition-colors">12m</button>
          <button className="px-4 py-1 text-[12px] font-medium font-sans text-white bg-[rgba(255,255,255,0.08)] rounded-full shadow-inner border border-[rgba(255,255,255,0.12)]">30d</button>
        </div>
      </div>

      <div className="flex-1 min-h-[220px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={MOCK_CHART_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.035)" />
            
            <XAxis 
              dataKey="pr" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#4A5070', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              dy={15}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#4A5070', fontSize: 11, fontFamily: 'DM Sans' }}
              domain={[0, 100]}
              dx={-10}
            />
            
            <RechartsTooltip cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} content={<CustomTooltip />} />

            <Line 
              type="monotone" 
              dataKey="security" 
              name="Security Risk"
              stroke="#FF2D6B" 
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: '#FF2D6B', stroke: '#0A0A12', strokeWidth: 2 }}
              style={{ filter: `drop-shadow(0 4px 6px rgba(255, 45, 107, 0.5))` }}
            />
            <Line 
              type="monotone" 
              dataKey="aiConfidence" 
              name="AI Confidence"
              stroke="#9B6DFF" 
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: '#9B6DFF', stroke: '#0A0A12', strokeWidth: 2 }}
              style={{ filter: `drop-shadow(0 4px 6px rgba(155, 109, 255, 0.45))` }}
            />
            <Line 
              type="monotone" 
              dataKey="reliability" 
              name="Reliability"
              stroke="#00D084" 
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, fill: '#00D084', stroke: '#0A0A12', strokeWidth: 2 }}
              style={{ filter: `drop-shadow(0 4px 6px rgba(0, 208, 132, 0.45))` }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-legend">
        <div className="legend-item"><span className="legend-dot bg-[#FF2D6B]" /> Security Risk</div>
        <div className="legend-item"><span className="legend-dot bg-[#9B6DFF]" /> AI Confidence</div>
        <div className="legend-item"><span className="legend-dot bg-[#00D084]" /> Reliability</div>
      </div>
    </div>
  )
}
