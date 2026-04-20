import { useState } from 'react'
import { sendChat } from '../api/client'

export default function ChatBox({ playerName, trust, onChatResponse }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!message.trim() || loading) return
    const text = message.trim()
    setMessage('')
    setLoading(true)
    try {
      const res = await sendChat(playerName, text)
      onChatResponse(res.data.response, trust)
    } catch {
      onChatResponse('*the dog looks confused*', trust)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-box">
      <div className="chat-input-row">
        <input
          type="text"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={loading ? 'Waiting for response...' : 'Say something to your dog...'}
          className="chat-input"
          disabled={loading}
        />
        <button
          className="chat-send-btn"
          onClick={handleSend}
          disabled={!message.trim() || loading}
        >
          {loading ? '...' : 'Talk'}
        </button>
      </div>
    </div>
  )
}
