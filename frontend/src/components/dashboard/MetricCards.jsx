import { useCountUp } from '../../hooks/useAnimations'

function MetricCardItem({ card, idx }) {
  const { count, ref } = useCountUp(card.value, 1500 + idx * 200)
  
  return (
    <div 
      ref={ref}
      className={`glass-1 metric-card ${card.active ? 'critical-active' : ''}`}
      style={{ '--i': idx }}
    >
      {card.live ? (
        <div className="flex justify-between items-start">
          <span className="live-badge">LIVE</span>
        </div>
      ) : (
        <div className="h-[22px]" /> /* Spacer if no badge */
      )}
      
      <div className="flex flex-col mt-auto gap-0.5">
        <span className={`metric-number ${card.colorClass}`}>
          {count}{card.suffix}
        </span>
        <span className="metric-label">{card.label}</span>
      </div>
    </div>
  )
}

export default function MetricCards() {
  const cards = [
    { label: 'PRs Scanned', value: 142, colorClass: 'metric-prs' },
    { label: 'Secrets Blocked', value: 38, colorClass: 'metric-secrets' },
    { label: 'Critical Findings', value: 67, colorClass: 'metric-critical', live: true, active: true },
    { label: 'Active Repos', value: 12, colorClass: 'metric-repos' },
    { label: 'Cost Savings', value: 90, colorClass: 'metric-savings', suffix: '%' },
    { label: 'Compliance Issues', value: 45, colorClass: 'metric-issues' },
  ]

  return (
    <>
      {cards.map((card, idx) => (
        <MetricCardItem key={card.label} card={card} idx={idx} />
      ))}
    </>
  )
}
