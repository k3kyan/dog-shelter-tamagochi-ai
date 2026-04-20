from pydantic import BaseModel

# remember, since backend handles stuff, the schemas (aka the api interactions) should not carry any stats (besides initial setup)
class DogAgentChatRequestSchema(BaseModel):
    player_name: str
    message: str