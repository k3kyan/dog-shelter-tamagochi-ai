from pydantic import BaseModel

class CareRequestSchema(BaseModel):
    player_name: str #will be how u will get breed, current_trust
    action: str    # "feed", "walk", "groom", "play", "talk"

class TickRequestSchema(BaseModel):
    player_name: str