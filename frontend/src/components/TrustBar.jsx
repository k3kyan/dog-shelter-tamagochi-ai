export default function TrustBar({ trust, trustStage, breed, personalityType }) {
  const stage = trustStage?.stage || 'withdrawn'
  const nameRevealed = trustStage?.name_revealed
  const personalityRevealed = trustStage?.personality_revealed

  const displayBreed = nameRevealed ? breed : '???'
  const displayPersonality = personalityRevealed ? personalityType : null

  const labels = {
    withdrawn: `??? is getting used to you...`,
    cautious:  `${displayBreed} is starting to trust you`,
    warming:   `${displayBreed} is opening up${displayPersonality ? ` — ${displayPersonality} emerging` : ''}`,
    thriving:  `${displayBreed}${displayPersonality ? ` — ${displayPersonality}` : ''} — fully trusting you`,
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
