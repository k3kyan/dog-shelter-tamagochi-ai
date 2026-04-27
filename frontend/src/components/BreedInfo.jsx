function TraitRow({ label, value, max = 1 }) {
  const pct = Math.round((value / max) * 100)
  const displayValue = `${Math.round(pct)}%`
  return (
    <div className="breed-trait-row">
      <span className="breed-trait-label">{label}</span>
      <div className="breed-trait-track">
        <div className="breed-trait-fill" style={{ width: `${pct}%` }} />
      </div>
      <span className="breed-trait-value">{displayValue}</span>
    </div>
  )
}

export default function BreedInfo({ gameState }) {
  return (
    <div className="breed-info">
      <h3 className="breed-info-title">About {gameState.breed}</h3>

      {gameState.description && (
        <p className="breed-info-text">{gameState.description}</p>
      )}

      {gameState.temperament && (
        <p className="breed-info-text">
          <strong>Temperament:</strong> {gameState.temperament}
        </p>
      )}

      <p className="breed-info-text">
        <strong>Avg. days in shelter:</strong> {Math.round(gameState.avg_days_in_shelter)}
      </p>

      <div className="breed-traits">
        <TraitRow label="Trainability"       value={gameState.trainability}       max={1} />
        <TraitRow label="Energy Level"       value={gameState.energy_level}       max={1} />
        <TraitRow label="Grooming Frequency" value={gameState.grooming_frequency} max={1} />
        <TraitRow label="Exercise Needs"     value={gameState.exercise_needs}     max={5} />
        <TraitRow label="Affectionate"       value={gameState.affectionate}       max={5} />
        <TraitRow label="Stranger Friendly"  value={gameState.stranger_friendly}  max={5} />
        <TraitRow label="Weight Gain Risk"   value={gameState.weight_gain_risk}   max={5} />
      </div>
    </div>
  )
}
