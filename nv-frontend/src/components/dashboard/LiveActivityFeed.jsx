import { useState, useEffect } from 'react'

const FEED_EVENTS = [
  { icon: '🔐', type: 'secret', text: 'Secret blocked in', boldText: 'acme/vibe-app PR #42', severity: 'critical', time: 2 },
  { icon: '🎭', type: 'hallucinated', text: 'Hallucinated pkg', boldText: 'openai-stream-helper', severity: 'high', time: 5 },
  { icon: '💉', type: 'secret', text: 'SQL injection found in', boldText: 'routes/users.js:28', severity: 'critical', time: 8 },
  { icon: '🛡️', type: 'hallucinated', text: 'SOC2 CC6.1 violation', boldText: 'mapped to SECRET', severity: 'high', time: 12 },
  { icon: '💬', type: 'hallucinated', text: 'Prompt injection vector in', boldText: 'routes/chat.js', severity: 'high', time: 15 },
  { icon: '🔀', type: 'hallucinated', text: 'Routed 7 prompts to Haiku', boldText: '— saved 90%', severity: 'info', time: 18 },
  { icon: '💥', type: 'secret', text: 'Exploit payload generated for', boldText: 'SQL finding', severity: 'critical', time: 22 },
  { icon: '🧠', type: 'hallucinated', text: 'Root cause:', boldText: 'Training data reproduction bias', severity: 'info', time: 25 },
  { icon: '📜', type: 'secret', text: 'Stripe key found in', boldText: 'git history config.js', severity: 'high', time: 28 },
  { icon: '🏗️', type: 'hallucinated', text: 'S3 bucket missing', boldText: 'BlockPublicAccess', severity: 'medium', time: 32 },
]

export default function LiveActivityFeed() {
  const [events, setEvents] = useState([])
  const [eventIndex, setEventIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setEventIndex(prev => {
        const next = prev + 1
        if (next > FEED_EVENTS.length) return 0
        return next
      })
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (eventIndex === 0) {
      setEvents([])
      return
    }
    setEvents(FEED_EVENTS.slice(0, eventIndex))
  }, [eventIndex])

  return (
    <div className="glass-1 live-card flex flex-col h-full overflow-hidden">
      <div className="flex items-center justify-between mb-4 border-b border-[var(--divider)] pb-4 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="live-header-dot" />
          <h3 className="text-section-title text-textPrimary ml-1.5">Live Activity</h3>
        </div>
        <span className="events-pill shadow-inner">
          {events.length} events
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar relative z-10">
        {events.length === 0 && (
          <div className="pt-10 text-center text-label">
            Waiting for activity stream...
          </div>
        )}
        {[...events].reverse().map((event, i) => (
          <div
            key={`${event.time}-${i}`}
            className="activity-row hover:bg-[rgba(255,255,255,0.015)] rounded-lg transition-colors duration-300"
            style={{
              animation: i === 0 ? 'glassIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)' : 'none',
            }}
          >
            {/* Event Icon / Badge */}
            <div className={`activity-icon ${event.type}`}>
              {event.icon}
            </div>

            {/* Event Content */}
            <div className="flex-1 min-w-0 flex flex-col justify-center">
              <div className="activity-text truncate">
                {event.text} <strong>{event.boldText}</strong>
              </div>
            </div>

            {/* Timestamp */}
            <div className="activity-time pt-[3px]">
              {event.time}s ago
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
