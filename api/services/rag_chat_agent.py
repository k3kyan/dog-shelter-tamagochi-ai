# RAG logic
# (this is similar to how i created the test_retreival.py) (lowkey im just referencing my test_retrieval.py bc i already did this)
# actually this file is a great summary of what i've learned in this project so far!!!! wowow yay. and its the last backend part too nice!!!
# Adjustments: chromadb and sentence-transformers/pytorch were too massive and causing lambda cold start 403 failures so i'm replacing chromadb=pinecone and sentence-transformers/torch with huggingface API
# import chromadb
# from sentence_transformers import SentenceTransformer #to retrieve (remember!! same embeddings!! cool stuff)
# from langchain_groq import ChatGroq #to chat
# import httpx
import os
from pinecone import Pinecone
from langchain_groq import ChatGroq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

# Old Notes:
# lazy singletons — delaying initializing these so Lambda can import my Python module since /tmp/chroma_db wont exist yet (which trying to initialize/create the chromadb would cause fail/crash)
# (lazy singletons is a design pattern + timing behavior)
# (singleton = create something once and reuse it everywhere (like a database client, cache, or heavy object u dont want to recreate over and over))
# (lazy (in "lazy singleton") = dont create it until you actually need it)
# (so aka lazy singleton = created once, but only when needed)
# (the FastAPI startup event downloads chroma_db from S3 first. these init on the first actual request)
# we have to do this way because it's how Lambda initializes its environment (cold start)
# _get_rag_resources() initializes them on the first request (after the startup event has already downloaded /tmp/chroma_db). 
# llm stays module-level since it's just a Groq API client with no local file dependency.
# _client = None
# _collection = None
# _embed_model = None

# def _get_rag_resources():
#     global _client, _collection, _embed_model
#     if _client is None:
#         # load chromaDB and embedding model 
#         # initialize ChromaDB client 
#         _client = chromadb.PersistentClient(
#             path=os.getenv('CHROMA_PATH', '../../ragpipeline/data/chroma_db')
#         )

#         # loads chromadb collection(table) with dataset name i chose in embed.py (contains text chunks (documents), embeddings, metadata)  
#         _collection = _client.get_collection('dog_care_articles')

# lazy singleton — Pinecone client initialized on first agent call
_index = None

def _get_pinecone_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        _index = pc.Index(os.getenv('PINECONE_INDEX', 'dog-shelter-tamagochi-ai'))
    return _index

# embed questions w huggingface inference api
# IMPORTANT: you must use the same model you used when storing embeddings!!!!!!!!
def _get_query_embedding(question: str) -> list:
    client = InferenceClient(token=os.getenv('HF_TOKEN', ''))
    result = client.feature_extraction(question, model='sentence-transformers/all-MiniLM-L6-v2')
    # no need to raise error bc hf inferenceclient handles raising exceptions before returning result (where before i had to raise it manually)
    # InferenceClient returns a numpy array. convert to plain list for Pinecone
    # check whether the result object has method called tolist()
    if hasattr(result, 'tolist'):
        return result.tolist() 
    else:
        return list(result)

# Initialize Groq LLM for generating responses for user
llm = ChatGroq(
    model='llama-3.1-8b-instant', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)

# the final piece of the RAG pattern: retrieving relevant context, then generating an informed answer using the LLM
def retrieve_and_answer(question: str, breed: str):
    # 1. embed player's question
    # IMPORTANT: convert query -> embedding (that actually makes a lot of sense!! how else are we supposed to map and compare vectors)
    index = _get_pinecone_index()
    embedding = _get_query_embedding(f"{breed}: {question}")

    # 2. find top 3 most similar chunks in ChromaDB
    results = index.query(
        vector=embedding, 
        top_k=3, #return top 3 matches
        include_metadata=True
        )

    context_docs = []
    for match in results.matches:
        context = match.metadata.get('context', '')
        chunk = match.metadata.get('chunk', '')
        if context:
            context_docs.append(f"{context}\n\n{chunk}")
        else:
            context_docs.append(chunk)

    context = '\n\n'.join(context_docs)

    # build a deduplicated set of source URLs from the Pinecone results
    seen = set()
    for m in results.matches:
        url = m.metadata.get('source_url', '')
        if url:
            seen.add(url) 
    sources = list(seen)

    # 3. generate informed response based on retrieved context
    prompt = f"""You are a helpful dog care advisor.
    A player is caring for a {breed} and asked: "{question}"

    Use ONLY this context to answer. Do not add outside knowledge: {context}

    Give a friendly, practical 2-3 sentence answer.
    If the context doesn't contain enough info, say so honestly.
    """

    # 4. call llm with this prompt and get a response!! yayay very cool
    # referenced embed.py generate_context()
    response = llm.invoke(prompt)
    cleaned_response = response.content.strip() #in case theres whitespace before/after string, since llm's frequently return texts with trailing whitespace
    return {
        'answer': cleaned_response,
        'sources': sources
    }