from pydantic import BaseModel

# for validating/typing API request data, not storing stuff
class AdopterProfileSchema(BaseModel):
    living_situation: str   # "apartment" or "house"
    climate: str            # "hot", "cold", or "mild"
    time_home: str          # "always", "sometimes", or "rarely"
    experience: str         # "first_time" or "experienced"

class StartGameSchema(BaseModel):
    player_name: str
    breed: str
    adopter_profile: dict

class PlayerProfileSchema(BaseModel):
    player_name: str
    breed: str
    adopter_profile: str
    hunger: str
    happiness: str
    energy: str
    health: str
    trust: str
    avg_days_in_shelter: str
    personality_type: str
    temperament: str
    energy_level: str
    trainability: str
    grooming_frequency: str
    weight_gain_risk: str
    exercise_needs: str
    affectionate: str
    stranger_friendly: str