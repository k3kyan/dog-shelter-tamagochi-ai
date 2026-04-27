import { useState } from 'react'
import { performCare } from '../api/client'

const ACTIONS = [
  { action: 'feed',  label: 'Feed',  icon: '🍖' },
  { action: 'walk',  label: 'Walk',  icon: '🦮' },
  { action: 'play',  label: 'Play',  icon: '🎾' },
  { action: 'rest',  label: 'Rest',  icon: '💤' },
]

export default function CareButtons({ playerName, trustStage, onUpdate }) {
  const [loading, setLoading] = useState(null)

  const handleCare = async (action) => {
    if (loading) return
    setLoading(action)
    try {
      const res = await performCare(playerName, action)
      onUpdate(res.data)
    } catch (e) {
      console.error('Care action failed:', e)
    } finally {
      setLoading(null)
    }
  }

  const isWithdrawn = trustStage?.stage === 'withdrawn'

  return (
    <div className="care-buttons">
      {isWithdrawn && (
        <p className="care-note">
          They might not be ready yet... but they still need care
        </p>
      )}
      <div className="care-grid">
        {ACTIONS.map(({ action, label, icon }) => (
          <button
            key={action}
            className="care-btn"
            onClick={() => handleCare(action)}
            disabled={loading !== null}
          >
            <span className="care-icon">{icon}</span>
            <span>{loading === action ? '...' : label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
