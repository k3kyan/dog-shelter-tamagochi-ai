from pydantic import BaseModel
from typing import Optional

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
    adopter_profile: dict
    hunger: float
    happiness: float
    energy: float
    health: float
    trust: float
    avg_days_in_shelter: float
    personality_type: str
    temperament: str
    energy_level: float
    trainability: float
    grooming_frequency: float
    weight_gain_risk: float
    exercise_needs: float
    affectionate: int
    stranger_friendly: int

class PlayerProfileUpdateSchema(BaseModel):
    hunger: Optional[float] = None
    happiness: Optional[float] = None
    energy: Optional[float] = None
    health: Optional[float] = None
    trust: Optional[float] = None
    energy_level: Optional[float] = None
    trainability: Optional[float] = None
    grooming_frequency: Optional[float] = None
    weight_gain_risk: Optional[float] = None
    exercise_needs: Optional[float] = None
    affectionate: Optional[int] = None
    stranger_friendly: Optional[int] = None