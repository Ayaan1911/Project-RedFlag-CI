import { getSeverityColor, getSeverityBg } from '../../utils/scoring'

export default function SeverityBadge({ severity }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(severity)} ${getSeverityBg(severity)}`}>
      {severity === 'CRITICAL' && '●'}
      {severity === 'HIGH' && '●'}
      {severity === 'MEDIUM' && '●'}
      {severity === 'LOW' && '○'}
      {severity}
    </span>
  )
}
