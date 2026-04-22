import { useState } from 'react'
import AdopterProfile from './components/AdopterProfile'
import ShelterScreen from './components/ShelterScreen'
import RescueScreen from './components/RescueScreen'
import './App.css'

export default function App() {
  const [screen, setScreen] = useState('adopter')
  const [playerName, setPlayerName] = useState('')
  const [adopterProfile, setAdopterProfile] = useState(null)
  const [breedScores, setBreedScores] = useState({})
  const [playerState, setPlayerState] = useState(null)

  const handleProfileComplete = (name, profile, scores) => {
    setPlayerName(name)
    setAdopterProfile(profile)
    setBreedScores(scores)
    setScreen('shelter')
  }

  const handleGameStart = (state) => {
    setPlayerState(state)
    setScreen('rescue')
  }

  const handleResume = (state) => {
    setPlayerState(state)
    setScreen('rescue')
  }

  return (
    <div className="app">
      {screen === 'adopter' && (
        <AdopterProfile
          onComplete={handleProfileComplete}
          onResume={handleResume}
        />
      )}
      {screen === 'shelter' && (
        <ShelterScreen
          playerName={playerName}
          adopterProfile={adopterProfile}
          breedScores={breedScores}
          onStart={handleGameStart}
          onBack={() => setScreen('adopter')}
        />
      )}
      {screen === 'rescue' && playerState && (
        <RescueScreen initialState={playerState} />
      )}
    </div>
  )
}
