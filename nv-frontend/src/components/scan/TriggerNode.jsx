import { Handle, Position } from 'reactflow'

export default function TriggerNode({ data }) {
  const { label = 'PR Opened', pr = '#42', repo = 'acme/vibe-app', branch = 'feat/chat-api' } = data

  return (
    <div className="relative rounded-xl bg-surface border border-green/30 px-5 py-4 min-w-[220px] glow-green">
      {/* No input handle — this is the entry node */}

      <div className="flex items-center gap-2 mb-2">
        <span className="status-dot bg-green scanning"></span>
        <span className="text-[13px] font-medium text-text">{label}</span>
      </div>

      <div className="space-y-1 text-[11px]">
        <div className="flex items-center gap-2">
          <span className="text-textDim">Repo</span>
          <span className="text-text">{repo}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-textDim">PR</span>
          <span className="text-green font-medium">{pr}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-textDim">Branch</span>
          <span className="text-textMuted">{branch}</span>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!w-2.5 !h-2.5 !bg-green !border-2 !border-green/50 !rounded-full"
      />
    </div>
  )
}
