# AI System: dog chat agent 
# langchain trust-aware dog chat agent
# NOT the rag system, uses the etl data + the game system logic (trust, care, etc)

# TODO: 
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool #tool = specialized, callable function that allows agent to interact with external world, like searching web, query databases, execute python code, or call apis, etc. tools enable real time data access.
import os, json 
from dotenv import load_dotenv
load_dotenv()

# Initialize Groq LLM for context generation
llm = ChatGroq(
    model='llama-3.1-8b-instant', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)


# Custom Tools for the dog chat agent ------------------------

# Tool 1: get current stats

# Tool 2: get breed facts

# Tool 3: suggest activity



# Trust stage system prompts ------------------------
# withdrawn, cautious, warming, thriving (prob make these enums bc i use this in the trust_system.py too)

# Agent executor function ------------------------
# build dog breed agent

# endpoints (in separate routes/dog_agent_routes.py file) ------------------------