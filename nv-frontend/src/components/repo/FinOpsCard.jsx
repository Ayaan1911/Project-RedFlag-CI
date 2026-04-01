import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { MOCK_FINOPS } from '../../api/repoMockData'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null
  return (
    <div className="bg-surface border border-border rounded-lg p-3 text-xs">
      <p className="text-text font-medium mb-1">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color }} className="flex justify-between gap-4">
          <span>{entry.name}</span>
          <span className="font-semibold">${entry.value.toFixed(4)}</span>
        </p>
      ))}
    </div>
  )
}

export default function FinOpsCard() {
  const finops = MOCK_FINOPS

  return (
    <div className="glass-1 p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-medium text-text">FinOps — Bedrock Cost Breakdown</h3>
          <p className="text-xs text-textMuted mt-0.5">Intelligent routing cost analysis</p>
        </div>
        <span className="text-xs text-green bg-greenDim px-2 py-0.5 rounded-full font-medium">
          {finops.savingsPercent}% saved
        </span>
      </div>

      {/* Cost Summary */}
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="bg-bg rounded-lg p-3 border border-border">
          <div className="text-[11px] text-textMuted mb-1">With Router</div>
          <div className="text-lg font-bold text-green">${finops.totalCost.toFixed(4)}</div>
        </div>
        <div className="bg-bg rounded-lg p-3 border border-border">
          <div className="text-[11px] text-textMuted mb-1">Without Router</div>
          <div className="text-lg font-bold text-textMuted line-through">${finops.totalWithoutRouting.toFixed(4)}</div>
        </div>
        <div className="bg-bg rounded-lg p-3 border border-border">
          <div className="text-[11px] text-textMuted mb-1">Total Saved</div>
          <div className="text-lg font-bold text-purple">${(finops.totalWithoutRouting - finops.totalCost).toFixed(4)}</div>
        </div>
      </div>

      {/* Model Breakdown */}
      <div className="flex gap-4 mb-5">
        {finops.modelBreakdown.map((m) => (
          <div key={m.model} className="flex items-center gap-2 text-xs">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: m.color }}></span>
            <span className="text-text">{m.model}</span>
            <span className="text-textDim">·</span>
            <span className="text-textMuted">{m.calls} calls</span>
            <span className="text-textDim">·</span>
            <span style={{ color: m.color }} className="font-medium">${m.cost.toFixed(4)}</span>
          </div>
        ))}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={finops.scanCostHistory} barCategoryGap="25%">
          <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1c" />
          <XAxis
            dataKey="scan"
            tick={{ fill: '#8b949e', fontSize: 11 }}
            axisLine={{ stroke: '#2a2a2a' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#8b949e', fontSize: 11 }}
            axisLine={{ stroke: '#2a2a2a' }}
            tickLine={false}
            tickFormatter={(v) => `$${v.toFixed(3)}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
            iconType="circle"
            iconSize={6}
          />
          <Bar dataKey="costNoRoute" name="Without Routing" fill="#2a2a2a" radius={[4, 4, 0, 0]} />
          <Bar dataKey="cost" name="With Routing" fill="#39d353" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
