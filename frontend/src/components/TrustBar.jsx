export default function TrustBar({ trust, trustStage, breed }) {
  const stage = trustStage?.stage || 'withdrawn'

  const labels = {
    withdrawn: `${breed} is getting used to you...`,
    cautious:  `${breed} is starting to trust you`,
    warming:   `${breed} is opening up`,
    thriving:  `${breed} now fully trusts you`,
  }
  const label = labels[stage] || `Getting to know each other...`

  const pct = Math.min(100, Math.max(0, Math.round(trust)))
  const color = pct < 33 ? '#ef4444' : pct < 66 ? '#f97316' : '#22c55e'

  return (
    <div className="trust-bar-container">
      <div className="trust-label">{label}</div>
      <div className="trust-bar-track">
        <div
          className="trust-bar-fill"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <div className="trust-value">Trust: {pct}/100</div>
    </div>
  )
}
