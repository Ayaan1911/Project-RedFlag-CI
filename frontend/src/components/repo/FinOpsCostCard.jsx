import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { MOCK_FINOPS } from '../../api/repoMockData'

export default function FinOpsCostCard() {
  const data = MOCK_FINOPS;
  
  return (
    <div className="glass-1 flex flex-col pt-6 px-7 pb-6 h-full" style={{ background: 'rgba(74,108,247,0.06)', border: '1px solid rgba(74,108,247,0.16)' }}>
      {/* Header */}
      <div className="flex justify-between items-start mb-5">
        <div>
          <h2 style={{ font: '600 17px var(--font-display)', color: '#F0F2FF' }}>FinOps — Bedrock Cost Breakdown</h2>
          <p style={{ font: '400 12px var(--font-body)', color: '#4A5070', marginTop: '2px' }}>Intelligent routing cost analysis</p>
        </div>
        <div style={{ background: 'rgba(0,208,132,0.15)', border: '1px solid rgba(0,208,132,0.28)', padding: '4px 12px', borderRadius: '999px', color: '#00D084', font: '700 12px var(--font-display)' }}>
          {data.savingsPercent}% saved
        </div>
      </div>

      {/* 3 cost sub-cards */}
      <div className="flex gap-3 mb-6">
        <div className="flex-1" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '12px', padding: '14px 16px' }}>
          <div style={{ font: '400 11px var(--font-body)', color: '#4A5070', marginBottom: '4px' }}>With Router</div>
          <div style={{ font: '700 28px var(--font-display)', color: '#00D084', textShadow: '0 0 20px rgba(0,208,132,0.35)', lineHeight: '1' }}>${data.totalCost.toFixed(4)}</div>
        </div>
        <div className="flex-1" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '12px', padding: '14px 16px' }}>
          <div style={{ font: '400 11px var(--font-body)', color: '#4A5070', marginBottom: '4px' }}>Without Router</div>
          <div style={{ font: '700 28px var(--font-display)', color: '#4A5070', textDecoration: 'line-through', textDecorationColor: 'rgba(255,255,255,0.20)', lineHeight: '1' }}>${data.totalWithoutRouting.toFixed(4)}</div>
        </div>
        <div className="flex-1" style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '12px', padding: '14px 16px' }}>
          <div style={{ font: '400 11px var(--font-body)', color: '#4A5070', marginBottom: '4px' }}>Total Saved</div>
          <div style={{ font: '700 28px var(--font-display)', color: '#9B6DFF', textShadow: '0 0 20px rgba(155,109,255,0.30)', lineHeight: '1' }}>${(data.totalWithoutRouting - data.totalCost).toFixed(4)}</div>
        </div>
      </div>
      
      {/* Legend Row */}
      <div className="flex gap-6 mb-5 px-1 flex-wrap">
        {data.modelBreakdown.map(m => (
          <div key={m.model} className="flex items-center gap-2">
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: m.color }} />
            <span style={{ font: '400 12px var(--font-body)', color: '#9AA0BC' }}>{m.model}</span>
            <span style={{ font: '400 12px var(--font-mono)', color: '#4A5070' }}>{m.calls} calls</span>
            <span style={{ font: '600 12px var(--font-mono)', color: m.color }}>${m.cost.toFixed(4)}</span>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div style={{ flexGrow: 1, width: '100%', minHeight: '130px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.scanCostHistory} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.035)" />
            <XAxis dataKey="scan" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#4A5070', fontFamily: 'var(--font-mono)' }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#4A5070', fontFamily: 'var(--font-mono)' }} />
            <Tooltip 
              cursor={{ fill: 'rgba(255,255,255,0.02)' }}
              contentStyle={{ background: 'rgba(10,10,18,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}
              itemStyle={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}
              labelStyle={{ fontFamily: 'var(--font-body)', fontSize: '13px', color: '#F0F2FF', marginBottom: '8px' }}
            />
            <Bar dataKey="costNoRoute" name="Without Routing" fill="rgba(74,108,247,0.35)" stroke="rgba(74,108,247,0.60)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="cost" name="With Routing" fill="rgba(0,208,132,0.50)" stroke="rgba(0,208,132,0.80)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
