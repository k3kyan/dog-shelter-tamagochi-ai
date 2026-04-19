from pydantic import BaseModel

# for validating/typing API request data, not storing stuff
class AdopterProfileSchema(BaseModel):
    living_situation: str   # "apartment" or "house"
    climate: str            # "hot", "cold", or "mild"
    time_home: str          # "always", "sometimes", or "rarely"
    experience: str         # "first_time" or "experienced"
