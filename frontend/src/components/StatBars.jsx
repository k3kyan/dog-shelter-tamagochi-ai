function StatBar({ label, value, icon, invert = false }) {
  const display = invert ? 100 - value : value
  const pct = Math.min(100, Math.max(0, display))
  const color = pct > 60 ? '#22c55e' : pct > 30 ? '#f59e0b' : '#ef4444'

  return (
    <div className="stat-bar">
      <div className="stat-header">
        <span>{icon} {label}</span>
        <span className="stat-value">{Math.round(pct)}</span>
      </div>
      <div className="stat-track">
        <div
          className="stat-fill"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}

export default function StatBars({ hunger, happiness, energy, health }) {
  return (
    <div className="stat-bars">
      <StatBar label="Hunger" icon="🍖" value={hunger} invert={true} />
      <StatBar label="Happiness" icon="😊" value={happiness} />
      <StatBar label="Energy" icon="⚡" value={energy} />
      <StatBar label="Health" icon="❤️" value={health} />
    </div>
  )
}
