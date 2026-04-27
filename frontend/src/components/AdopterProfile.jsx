import { useState } from 'react'
import { matchBreeds, getPlayerState } from '../api/client'

const QUESTIONS = [
  {
    key: 'living_situation',
    label: 'Where do you live?',
    options: [
      { value: 'apartment', label: 'Apartment' },
      { value: 'house', label: 'House' },
    ],
  },
  {
    key: 'climate',
    label: 'Your climate?',
    options: [
      { value: 'hot', label: 'Hot' },
      { value: 'mild', label: 'Mild' },
      { value: 'cold', label: 'Cold' },
    ],
  },
  {
    key: 'time_home',
    label: 'How often are you home?',
    options: [
      { value: 'always', label: 'Always' },
      { value: 'sometimes', label: 'Sometimes' },
      { value: 'rarely', label: 'Rarely' },
    ],
  },
  {
    key: 'experience',
    label: 'Dog experience?',
    options: [
      { value: 'first_time', label: 'First Time' },
      { value: 'experienced', label: 'Experienced' },
    ],
  },
]

export default function AdopterProfile({ onComplete, onResume }) {
  const [playerName, setPlayerName] = useState('')
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const allAnswered = QUESTIONS.every(q => answers[q.key])
  const canSubmit = playerName.trim() && allAnswered

  const handleFindMatch = async () => {
    if (!canSubmit || loading) return
    setLoading(true)
    setError('')
    try {
      const profile = {
        living_situation: answers.living_situation,
        climate: answers.climate,
        time_home: answers.time_home,
        experience: answers.experience,
      }
      const res = await matchBreeds(profile)
      onComplete(playerName.trim(), profile, res.data)
    } catch {
      setError('Something went wrong. Is the server running?')
    } finally {
      setLoading(false)
    }
  }

  const handleResume = async () => {
    if (!playerName.trim()) {
      setError('Enter your player name to resume.')
      return
    }
    setLoading(true)
    setError('')
    try {
      const res = await getPlayerState(playerName.trim())
      onResume(res.data)
    } catch (e) {
      if (e.response?.status === 404) {
        setError(`No game found for "${playerName.trim()}". Start a new game below.`)
      } else {
        setError('Could not connect to the server.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="adopter-profile">
      <h1>Kelly Y's Dog Adoption Simulator</h1>
      <p className="subtitle">Find your perfect rescue match, practice raising them, and chat!</p>

      <div className="name-section">
        <label className="name-label">What would you like to be called?</label>
        <div className="name-row">
          <input
            type="text"
            value={playerName}
            onChange={e => setPlayerName(e.target.value)}
            placeholder="Your name..."
            className="name-input"
            maxLength={32}
          />
          <button
            className="resume-btn"
            onClick={handleResume}
            disabled={loading || !playerName.trim()}
          >
            Resume game
          </button>
        </div>
      </div>

      <div className="questions">
        {QUESTIONS.map(q => (
          <div key={q.key} className="question">
            <p className="question-label">{q.label}</p>
            <div className="options">
              {q.options.map(opt => (
                <button
                  key={opt.value}
                  className={`option-btn${answers[q.key] === opt.value ? ' selected' : ''}`}
                  onClick={() => setAnswers(prev => ({ ...prev, [q.key]: opt.value }))}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      <button
        className="primary-btn"
        onClick={handleFindMatch}
        disabled={!canSubmit || loading}
      >
        {loading ? 'Finding matches...' : 'Find my match'}
      </button>
    </div>
  )
}
