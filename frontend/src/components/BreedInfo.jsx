function TraitBar({ label, value, max = 1 }) {
  const pct = Math.round((value / max) * 100)
  return (
    <div className="breed-trait-bar">
      <div className="breed-trait-header">
        <span>{label}</span>
        <span className="breed-trait-value">{max === 1 ? `${Math.round(pct)}%` : `${Math.round(value)}/${max}`}</span>
      </div>
      <div className="stat-track">
        <div className="stat-fill" style={{ width: `${pct}%`, backgroundColor: '#a78bfa' }} />
      </div>
    </div>
  )
}

export default function BreedInfo({ gameState }) {
  return (
    <div className="breed-info">
      <h3 className="breed-info-title">About {gameState.breed}</h3>

      {gameState.description && (
        <p className="breed-description">{gameState.description}</p>
      )}

      {gameState.temperament && (
        <p className="breed-temperament"><strong>Temperament:</strong> {gameState.temperament}</p>
      )}

      <p className="breed-shelter-days">
        Average days in shelter: <strong>{Math.round(gameState.avg_days_in_shelter)}</strong>
      </p>

      <div className="breed-traits">
        <TraitBar label="Trainability"        value={gameState.trainability}       max={1} />
        <TraitBar label="Energy Level"        value={gameState.energy_level}       max={1} />
        <TraitBar label="Grooming Frequency"  value={gameState.grooming_frequency} max={1} />
        <TraitBar label="Exercise Needs"      value={gameState.exercise_needs}     max={5} />
        <TraitBar label="Affectionate"        value={gameState.affectionate}       max={5} />
        <TraitBar label="Stranger Friendly"   value={gameState.stranger_friendly}  max={5} />
        <TraitBar label="Weight Gain Risk"    value={gameState.weight_gain_risk}   max={5} />
      </div>
    </div>
  )
}
