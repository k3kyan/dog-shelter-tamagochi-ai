import { useState } from 'react'
import { askCareGuide } from '../api/client'

export default function CareGuide({ playerName, breed }) {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState(null)
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)

  const handleAsk = async () => {
    if (!question.trim() || loading) return
    setLoading(true)
    setAnswer(null)
    setSources([])
    try {
      const res = await askCareGuide(playerName, question.trim())
      setAnswer(res.data.answer)
      setSources(res.data.sources || [])
    } catch {
      setAnswer('Could not get an answer. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="care-guide">
      <div className="care-guide-title">📖 Care Guide — Ask about {breed}</div>

      <div className="care-guide-input-row">
        <input
          type="text"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleAsk()}
          placeholder="Ask a care question..."
          className="care-guide-input"
          disabled={loading}
        />
        <button
          className="care-guide-ask-btn"
          onClick={handleAsk}
          disabled={!question.trim() || loading}
        >
          {loading ? 'Searching...' : 'Ask'}
        </button>
      </div>

      {loading && <p className="care-guide-loading">Looking through care guides...</p>}

      {answer && (
        <div className="care-guide-answer">
          <p>{answer}</p>
          {sources.length > 0 && (
            <div className="care-guide-sources">
              <small>Sources:</small>
              <ul className="care-guide-source-list">
                {sources.map((url, i) => (
                  <li key={i}>
                    <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
