import { useState, useEffect } from 'react'
import { getBreeds, startGame } from '../api/client'

function getCompatibilityBadge(score) {
  if (score >= 90) return 'Perfect match'
  if (score >= 70) return 'Great match'
  if (score >= 50) return 'Good match'
  return null
}

export default function ShelterScreen({ playerName, adopterProfile, breedScores, onStart, onBack }) {
  const [breeds, setBreeds] = useState([]) // [{breed, avg_days_in_shelter}]
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    getBreeds()
      .then(res => {
        setBreeds(res.data)
        setLoading(false)
      })
      .catch(() => {
        setError('Could not load breeds. Is the server running?')
        setLoading(false)
      })
  }, [])

  const sortedBreeds = [...breeds].sort((a, b) => {
    return (breedScores[b.breed] ?? 0) - (breedScores[a.breed] ?? 0)
  })

  const handleBreedClick = async (breed) => {
    if (starting) return
    setStarting(breed)
    setError('')
    try {
      const res = await startGame(playerName, breed, adopterProfile)
      onStart(res.data)
    } catch (e) {
      if (e.response?.status === 409) {
        setError(e.response.data.detail)
      } else {
        setError('Could not start game. Is the server running?')
      }
      setStarting(null)
    }
  }

  if (loading) return <div className="loading-screen">Loading breeds...</div>

  return (
    <div className="shelter-screen">
      <div className="shelter-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <h1>Shelter Dogs</h1>
        <p>Hello, {playerName}! Choose a dog to rescue.</p>
      </div>

      {error && <p className="error shelter-error">{error}</p>}

      <div className="breed-grid">
        {sortedBreeds.map(({ breed, avg_days_in_shelter }) => {
          const score = breedScores[breed]
          const badge = score !== undefined ? getCompatibilityBadge(score) : null

          return (
            <button
              key={breed}
              className={`breed-card${starting === breed ? ' loading' : ''}`}
              onClick={() => handleBreedClick(breed)}
              disabled={starting !== null}
            >
              <div className="breed-name">{breed}</div>
              {avg_days_in_shelter !== undefined && (
                <div className="breed-days">
                  Waited avg {Math.round(avg_days_in_shelter)} days in shelter
                </div>
              )}
              {badge && <div className="breed-badge">{badge}</div>}
              {starting === breed && <div className="breed-loading">Starting...</div>}
            </button>
          )
        })}
      </div>
    </div>
  )
}
