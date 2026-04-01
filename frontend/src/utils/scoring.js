/**
 * Get Tailwind color class for a risk score
 */
export function getScoreColor(score) {
  if (score >= 81) return 'text-red';
  if (score >= 61) return 'text-amber';
  if (score >= 31) return 'text-amber';
  if (score >= 11) return 'text-green';
  return 'text-green';
}

export function getScoreBg(score) {
  if (score >= 81) return 'bg-redDim';
  if (score >= 61) return 'bg-amberDim';
  if (score >= 31) return 'bg-amberDim';
  return 'bg-greenDim';
}

export function getRiskLabel(score) {
  if (score >= 81) return 'CRITICAL';
  if (score >= 61) return 'HIGH RISK';
  if (score >= 31) return 'MODERATE';
  if (score >= 11) return 'LOW RISK';
  return 'SAFE';
}

export function getSeverityColor(severity) {
  const map = {
    CRITICAL: 'text-red',
    HIGH: 'text-amber',
    MEDIUM: 'text-blue',
    LOW: 'text-textMuted',
  };
  return map[severity] || 'text-textMuted';
}

export function getSeverityBg(severity) {
  const map = {
    CRITICAL: 'bg-redDim',
    HIGH: 'bg-amberDim',
    MEDIUM: 'bg-blue/10',
    LOW: 'bg-surfaceAlt',
  };
  return map[severity] || 'bg-surfaceAlt';
}

export function formatTimestamp(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}
