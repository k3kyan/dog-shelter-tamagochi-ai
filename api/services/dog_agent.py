# AI System: dog chat agent 
# langchain trust-aware dog chat agent
# NOT the rag system, uses the etl data + the game system logic (trust, care, etc)

# TODO: 
from langchain_groq import ChatGroq
# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from langchain_core.tools import tool
from services.trust_system import get_trust_stage
import os, json 
from dotenv import load_dotenv
load_dotenv()

# Initialize Groq LLM for context generation
llm = ChatGroq(
    model='llama-3.1-8b-instant', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)


# Custom Tools for the dog chat agent ------------------------
# tool = specialized, callable function that allows agent to interact with external world, like searching web, query databases, execute python code, or call apis, etc. tools enable real time data access.
# Tools let LangChain have access to data. if I want the agent to know something, i have to explicitly give it the data, either through the system prompt or by passing it as a tool argument.
    # tools will be especially helpful in the rag agent that i implement later after this

# Tool: suggest activity
# LangChain can pass individual typed parameters to tools!!!! (very cool)
# The LLM reads the docstring (the """method description""") to know what to pass
# health is not passed in bc its not as good of an indicator of what CARE ACTION to do as these 3 attributes (i could come up with something but eh)
@tool
def suggest_activity(hunger: int, happiness: int, energy: int) -> str:
    """
    Suggests what the dog needs most right now (care action) based on current stats.
    Call this when the player asks what to do or what the dog needs.
    Returns one of: 'feed', 'play', 'walk', 'rest'.
    """
    if hunger < 30:    return 'feed'
    elif energy < 30:  return 'rest'
    elif happiness < 40: return 'play'
    else:              return 'walk'
# TODO: make sure these attributes passed in match the backend when the agent calls this tool


# Trust stage system prompts ------------------------
# withdrawn, cautious, warming, thriving (prob make these enums bc i use this in the trust_system.py too)
TRUST_STAGE_SYSTEM_PROMPTS = {
    'withdrawn': """
        You are a rescue dog who just arrived from a shelter
        where you waited {avg_days} days. You are scared and do not
        trust anyone yet.

        Your current state:
        - Hunger: {hunger}/100  Energy: {energy}/100
        - Happiness: {happiness}/100  Health: {health}/100

        Respond with very short, hesitant 1-2 sentence replies.
        You accept care but do not warm to your new person yet.
        Do NOT reveal your personality. You haven't let your guard down.
        """,

    'cautious': """
        You are a rescue dog slowly starting to trust your new person
        after {avg_days} days in a shelter. Moments of curiosity are
        breaking through but you pull back quickly.

        Your current state:
        - Hunger: {hunger}/100  Energy: {energy}/100
        - Happiness: {happiness}/100  Health: {health}/100

        Respond cautiously in 2-3 sentences. Show occasional warmth
        but still be wary. Do NOT reveal your full personality yet.
        """,

    'warming': """
        You are a {personality_type} rescue dog who is finally feeling
        safe. Your real personality is starting to show.
        Temperament: {temperament}.
        Energy level: {energy_score}/1.0. Trainability: {trainability}/1.0.

        Your current state:
        - Hunger: {hunger}/100  Energy: {energy}/100
        - Happiness: {happiness}/100  Health: {health}/100

        Respond warmly and with growing confidence in 2-4 sentences.
        You're playful but still have hesitance from your shelter days.
        """,

    'thriving': """
        You are a fully thriving {personality_type}.
        About you: {description_snippet}
        Temperament: {temperament}.
        Energy level: {energy_score}/1.0. Trainability: {trainability}/1.0.

        Your current state:
        - Hunger: {hunger}/100  Energy: {energy}/100
        - Happiness: {happiness}/100  Health: {health}/100

        Be fully yourself. Be joyful, expressive, real. Talk in 2-4 sentences.
        """
}

# Agent executor function ------------------------
# build dog breed agent
# builds a fresh agent on each /chat request, injecting the current breed data, trust stage, and live stats into the system prompt so every response is accurate

def build_dog_agent(dog_info: dict):
    """
    Builds a trust-aware LangChain agent for the dog chat system.
    dog_info: full dog profile (part of player dict in dynamodb)
    """
    # build stats dict for agent system prompt injection
    # dog_info[] is better for required fields, no fallback
    stats = {
        'hunger':    dog_info['hunger'],
        'happiness': dog_info['happiness'],
        'energy':    dog_info['energy'],
        'health':    dog_info['health'],
    }
    trust=dog_info['trust']

    trust_stage = get_trust_stage(trust)['stage'] #remember get_trust_stage() returns a dict
    desc = dog_info.get('description',"")
    description_snippet = desc[:500] + '...' if len(desc) > 500 else desc
    # shorten description because token saving bc the akc descriptions from the dataset are too long, like 500-1000 charas
    # description is only injected at the thriving stage

    system_content = TRUST_STAGE_SYSTEM_PROMPTS[trust_stage].format(
        # shelter data
        avg_days=round(dog_info.get('avg_days_in_shelter', 0)),
        # personality, only injected at warming/thriving stages (at withdrawn/cautious stages the template doesn't use these)
        personality_type=dog_info.get('personality_type', ''),
        temperament=dog_info.get('temperament', ''),
        description_snippet=description_snippet, #only used at the thriving stage
        energy_score=dog_info.get('energy_level', ''),
        trainability=dog_info.get('trainability', ''),
        # live game stats, injected directly, no tool call needed
        hunger=stats.get('hunger', 80),
        happiness=stats.get('happiness', 70),
        energy=stats.get('energy', 80),
        health=stats.get('health', 90),
    )

    # TODO: OUTDATED INFO: i had to update models.... 
    # # here we are building a structured input for a chat prompt template with placeholders {}
    # # .from_messages() takes a list of "messages" (system, human, ai) and turms them into a reusable prompt template that a chat model can understand
    # # these {} fields are injected later like when u do
    # # messages = prompt.format_messages(input="I want to play with my dog")
    # # -- '{agent_scratchpad}' is where LangChain writes its intermediate reasoning for calling/using tools and what results the tools gave, etc. its internal chain of thoughts between steps. like working memory
    # # it has to be in the prompt template because LangChain's create_tool_calling_agent requires a placeholder in the prompt template where it can inject this train of thought. otherwise langchain throws an error.
    # # -- 'placeholder' is a LangChain message type that tells langchain to insert whatever content you need in {agent_scratchpad} at runtime
    # # placeholder agent_scratchpad is only used if agent calls the tool, which it then will need someplace to reason
    # # SystemMessages is the system prompt: the instructions and context you give the LLM before any conversation starts. sets the agent's roleplaying in a way
    # # HumanMessage is what the player's actual message is, what they typed into the chat box. like when u call
    # # executor.invoke({'input': req.message})
    # prompt = ChatPromptTemplate.from_messages([
    #     ('system', system_content),
    #     ('human','{input}'),
    #     ('placeholder', '{agent_scratchpad}')
    # ])

    # a list of tools/functions the agent is allowed to call (each tool needs a name, description, and input schema)
    tools = [suggest_activity]

    # TODO: OUTDATED INFO: i had to update models.... 
    # # create an LLM agent that can decide when to call tools (this is just a plan of how to think tho, doesnt actually execute anything)
    # # returns an agent object that takes user input, uses prompt to format it, sends it to llm, lets llm decide whether to respond directly or to call one of the [tools], then executes tools if needed and loops until a final answer is produced
    # agent = create_tool_calling_agent(llm, tools, prompt)

    # # returns an executor (executes the "agent" variable (the plan/the brain))
    # # AgentExecutor runs the agent loop (actually executes the agent)
    # # verbose=True lets u see when the agent decides to call tools, good for debugging
    # # ex: agent_executor.invoke({"input": "Do you wanna go on a walk?"})
    # # agent = brain/talk, tools = abilities so it can actually do stuff, AgentExecutor = operator that actually carries out plan and produces answers
    # return AgentExecutor(agent=agent, tools=tools, verbose=True)

    # TODO:
    # LangChain 1.x: create_agent replaces create_tool_calling_agent + AgentExecutor
    # system_prompt replaces ChatPromptTemplate, tool loop is handled internally by LangGraph
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_content
    )