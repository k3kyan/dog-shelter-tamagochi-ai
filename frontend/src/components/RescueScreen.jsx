import { useState, useEffect, useRef } from 'react'
import { tick } from '../api/client'
import TrustBar from './TrustBar'
import AsciiDog from './AsciiDog'
import StatBars from './StatBars'
import CareButtons from './CareButtons'
import ChatBox from './ChatBox'
import CareGuide from './CareGuide'

const TICK_INTERVAL = 30000

const DEFAULT_TRUST_STAGE = {
  stage: 'withdrawn',
  personality_revealed: false,
  name_revealed: false,
  ascii_mood: 'scared',
}

export default function RescueScreen({ initialState }) {
  const [gameState, setGameState] = useState(initialState)
  const [chatBubble, setChatBubble] = useState(null)
  const [chatHappy, setChatHappy] = useState(false)
  const [guideOpen, setGuideOpen] = useState(false)
  const [toasts, setToasts] = useState([])
  const prevTrustRef = useRef(initialState.trust)
  const chatBubbleTimer = useRef(null)

  const addToast = (message) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message }])
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000)
  }

  const checkTrustMilestones = (newTrust, state) => {
    const prev = prevTrustRef.current
    if (prev < 30 && newTrust >= 30) addToast('They peeked at you')
    if (prev < 60 && newTrust >= 60) addToast(`${state.personality_type} revealed!`)
    if (prev < 85 && newTrust >= 85) addToast(`${state.breed} fully trusts you :D`)
    prevTrustRef.current = newTrust
  }

  // Tick interval — backend calculates drain, no local stat math
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await tick(gameState.player_name)
        const data = res.data
        setGameState(data)
        checkTrustMilestones(data.trust, data)
      } catch (e) {
        console.error('Tick failed:', e)
      }
    }, TICK_INTERVAL)
    return () => clearInterval(interval)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameState.player_name])

  const handleCareUpdate = (data) => {
    setGameState(data)
    checkTrustMilestones(data.trust, data)
  }

  const handleChatResponse = (response, trustAtSend) => {
    if (chatBubbleTimer.current) clearTimeout(chatBubbleTimer.current)
    setChatBubble(response)
    chatBubbleTimer.current = setTimeout(() => setChatBubble(null), 10000)

    if (trustAtSend > 60) {
      setChatHappy(true)
      setTimeout(() => setChatHappy(false), 3000)
    }
  }

  const getMood = () => {
    if (chatHappy) return 'happy'
    if (gameState.health < 20) return 'sick'
    if (gameState.hunger > 90) return 'sad'
    if (gameState.happiness < 20) return 'sad'
    const backendMood = gameState.trust_stage?.ascii_mood || 'scared'
    // warming stage returns 'happy' from backend — map to 'curious' for default display
    // so 'happy' (^.^) is reserved for the post-chat happy moment
    if (backendMood === 'happy') return 'curious'
    return backendMood
  }

  const trustStage = gameState.trust_stage || DEFAULT_TRUST_STAGE

  return (
    <div className="rescue-screen">
      <div className="toasts">
        {toasts.map(t => (
          <div key={t.id} className="toast">{t.message}</div>
        ))}
      </div>

      <TrustBar
        trust={gameState.trust}
        trustStage={trustStage}
        breed={gameState.breed}
        personalityType={gameState.personality_type}
      />

      <div className="rescue-main">
        <div className="rescue-left">
          <AsciiDog mood={getMood()} chatBubble={chatBubble} />
          <ChatBox
            playerName={gameState.player_name}
            trust={gameState.trust}
            onChatResponse={handleChatResponse}
          />
        </div>

        <div className="rescue-right">
          <StatBars
            hunger={gameState.hunger}
            happiness={gameState.happiness}
            energy={gameState.energy}
            health={gameState.health}
          />
          <CareButtons
            playerName={gameState.player_name}
            trustStage={trustStage}
            onUpdate={handleCareUpdate}
          />
        </div>
      </div>

      <button className="guide-btn" onClick={() => setGuideOpen(true)} title="Care Guide">
        Care Guide
      </button>

      <CareGuide
        playerName={gameState.player_name}
        breed={trustStage.name_revealed ? gameState.breed : '???'}
        isOpen={guideOpen}
        onClose={() => setGuideOpen(false)}
      />
    </div>
  )
}
