import { MOCK_REPO } from '../../api/repoMockData'
import { getScoreColor, getRiskLabel } from '../../utils/scoring'
import { formatTimestamp } from '../../utils/scoring'

export default function RepoHeader() {
  const repo = MOCK_REPO

  return (
    <div className="glass-1 p-5 flex items-center gap-6 flex-wrap">
      {/* Repo Icon */}
      <div className="w-12 h-12 rounded-xl bg-surfaceAlt border border-border flex items-center justify-center text-2xl">
        📁
      </div>

      {/* Repo Info */}
      <div className="flex-1 min-w-0">
        <h1 className="text-xl font-semibold text-text">{repo.name}</h1>
        <p className="text-sm text-textMuted mt-0.5">{repo.description}</p>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="text-center px-3">
          <div className={`text-2xl font-bold ${getScoreColor(repo.techDebtScore)}`}>
            {repo.techDebtScore}
          </div>
          <div className="text-[11px] text-textMuted">Vibe Debt</div>
        </div>

        <div className="w-px h-10 bg-border"></div>

        <div className="text-center px-3">
          <div className="text-2xl font-bold text-purple">{repo.vibeCodeRatio}%</div>
          <div className="text-[11px] text-textMuted">AI-Generated</div>
        </div>

        <div className="w-px h-10 bg-border"></div>

        <div className="text-center px-3">
          <div className="text-2xl font-bold text-blue">{repo.totalScans}</div>
          <div className="text-[11px] text-textMuted">Total Scans</div>
        </div>

        <div className="w-px h-10 bg-border"></div>

        <div className="flex flex-col items-center px-3">
          <span className="text-xs bg-surfaceAlt text-textMuted px-2 py-0.5 rounded-full border border-border">
            {repo.language}
          </span>
          <div className="text-[11px] text-textMuted mt-1">{formatTimestamp(repo.lastScan)}</div>
        </div>
      </div>
    </div>
  )
}
