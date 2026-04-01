import { Handle, Position } from 'reactflow'

const statusColors = {
  idle: { dot: 'bg-textDim', border: 'border-border', bg: 'bg-surface' },
  scanning: { dot: 'bg-green scanning', border: 'border-green/40', bg: 'bg-surface' },
  done: { dot: 'bg-green', border: 'border-border', bg: 'bg-surface' },
  error: { dot: 'bg-red', border: 'border-red/40', bg: 'bg-surface' },
  critical: { dot: 'bg-red', border: 'border-red/30', bg: 'bg-surface' },
}

export default function ScannerNode({ data }) {
  const { label, status = 'done', findings = 0, icon = '🔍', description = '' } = data
  const style = statusColors[status] || statusColors.done

  const isCritical = status === 'critical' || findings > 2

  return (
    <div className={`relative rounded-xl ${style.bg} ${style.border} border px-4 py-3 min-w-[210px] max-w-[240px] transition-all duration-300 ${isCritical ? 'glow-pulse-red' : ''}`}>
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-2.5 !h-2.5 !bg-blue !border-2 !border-blue/50 !rounded-full"
      />

      {/* Header */}
      <div className="flex items-center gap-2 mb-1.5">
        <span className={`status-dot ${style.dot}`}></span>
        <span className="text-[13px] font-medium text-text truncate flex-1">{label}</span>
        <span className="text-sm">{icon}</span>
      </div>

      {/* Description */}
      {description && (
        <p className="text-[11px] text-textMuted mb-2 leading-relaxed">{description}</p>
      )}

      {/* Findings bar */}
      {findings > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className={`text-xs font-medium ${
              findings >= 3 ? 'text-red' : findings >= 1 ? 'text-amber' : 'text-textMuted'
            }`}>
              {findings} finding{findings !== 1 ? 's' : ''}
            </span>
          </div>
          <div className="h-1 bg-surfaceAlt rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${
                findings >= 3 ? 'bg-red' : findings >= 1 ? 'bg-amber' : 'bg-green'
              }`}
              style={{ width: `${Math.min(findings * 20, 100)}%` }}
            ></div>
          </div>
        </div>
      ) : status === 'done' ? (
        <span className="text-[11px] text-green">✓ Clean</span>
      ) : null}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-green !border-2 !border-green/50 !rounded-full"
      />
    </div>
  )
}
