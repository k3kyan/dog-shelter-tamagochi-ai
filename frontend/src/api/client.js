import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const getBreeds = () => axios.get(`${BASE_URL}/breeds`)
export const getBreed = (b) => axios.get(`${BASE_URL}/breeds/${encodeURIComponent(b)}`)

export const matchBreeds = (profile) => axios.post(`${BASE_URL}/player/match`, profile)
export const startGame = (player_name, breed, adopter_profile) =>
  axios.post(`${BASE_URL}/player/start`, { player_name, breed, adopter_profile })
export const getPlayerState = (player_name) =>
  axios.get(`${BASE_URL}/player/${encodeURIComponent(player_name)}`)

export const performCare = (player_name, action) =>
  axios.post(`${BASE_URL}/care`, { player_name, action })
export const tick = (player_name) =>
  axios.post(`${BASE_URL}/care/tick`, { player_name })

export const sendChat = (player_name, message) =>
  axios.post(`${BASE_URL}/agent/chat`, { player_name, message })
export const askCareGuide = (player_name, question) =>
  axios.post(`${BASE_URL}/agent/care-guide`, { player_name, question })
