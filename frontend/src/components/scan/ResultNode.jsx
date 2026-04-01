import { Handle, Position } from 'reactflow'

export default function ResultNode({ data }) {
  const {
    score = 0,
    label = 'Result',
    sublabel = '',
    icon = '📊',
    scoreColor = 'text-red'
  } = data

  return (
    <div className="relative rounded-xl bg-surface border border-border px-5 py-4 min-w-[220px] max-w-[260px]">
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-textDim !border-2 !border-border !rounded-full"
      />

      <div className="flex items-center gap-2 mb-3">
        <span className="text-lg">{icon}</span>
        <span className="text-[13px] font-medium text-text">{label}</span>
      </div>

      {/* Score ring */}
      <div className="flex items-center gap-3">
        <div className="relative w-14 h-14">
          <svg viewBox="0 0 48 48" className="w-14 h-14 -rotate-90">
            <circle cx="24" cy="24" r="20" fill="none" stroke="#2a2a2a" strokeWidth="3" />
            <circle
              cx="24" cy="24" r="20" fill="none"
              stroke={score >= 81 ? '#E63946' : score >= 61 ? '#f0a500' : score >= 31 ? '#f0a500' : '#39d353'}
              strokeWidth="3"
              strokeDasharray={`${(score / 100) * 125.6} 125.6`}
              strokeLinecap="round"
              className="transition-all duration-1000"
            />
          </svg>
          <span className={`absolute inset-0 flex items-center justify-center text-sm font-bold ${scoreColor}`}>
            {score}
          </span>
        </div>
        <div>
          <div className={`text-lg font-bold ${scoreColor}`}>{score}/100</div>
          {sublabel && <div className="text-[11px] text-textMuted">{sublabel}</div>}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-textDim !border-2 !border-border !rounded-full"
      />
    </div>
  )
}
