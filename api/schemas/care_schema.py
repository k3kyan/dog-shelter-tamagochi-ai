from pydantic import BaseModel

class CareRequestSchema(BaseModel):
    breed: str #to determine trust multiplier
    action: str
    current_trust: float
