from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger
from services.dog_agent import build_dog_agent
from services.player_service import get_player
from schemas.agent_schemas import DogAgentChatRequestSchema

agent_router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)

# Fetches player state from DynamoDB, runs agent 
@agent_router.post('/chat')
def chat(req: DogAgentChatRequestSchema):
    player = get_player(req.player_name)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')


    # TODO-Maybe: INTERESTING: Note: LangChain agents are stateless by default (aka it has no memory of previous convos), 
    # if we wanted convo memory, we can do ConversationBufferMemory or RunnableWithMessageHistory, but for this game we dont rly need that. plus there'd be a storage issue of where to store that info nah
    # but itd be cool bc the dog could remember things like "You told me you like playing with me!" which is cool but maybe i will add that later (if i want resume to be cooler)
        # PROBLEM: but with an AgentExecutor remembering convo memory, thats still a problem in this project 
        # bc u have to inject the new game data, otherwise the AgentExecutor just has stale data. 
        # But these dynamic stats are baked into the system prompt at AgentExecutor construction time. we have no mechanism to refresh these values without rebuilding the AgentExecutor.
            #POTENTIAL-SOLUTION: tools..?

    # IMPORTANT: Instead of reusing an AgentExecutor, since we have changing game data, we dont want AgentExecutor to have stale outdated info
    # so we have to call a fresh agent every time with the current game stats

    # build_dog_agent() returns AgentExecutor object yay!
    # player dict also holds the info for their dog, just confusing wording, i could prob improve in future eh
    executor = build_dog_agent(
        dog_info=player
    )
    result = executor.invoke({'input': req.message})
    return {'response': result['output']}
