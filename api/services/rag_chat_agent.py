# RAG logic
# (this is similar to how i created the test_retreival.py) (lowkey im just referencing my test_retrieval.py bc i already did this)
# actually this file is a great summary of what i've learned in this project so far!!!! wowow yay. and its the last backend part too nice!!!
import chromadb
from sentence_transformers import SentenceTransformer #to retrieve (remember!! same embeddings!! cool stuff)
from langchain_groq import ChatGroq #to chat
import os
from dotenv import load_dotenv
load_dotenv()

# lazy singletons — delaying initializing these so Lambda can import my Python module since /tmp/chroma_db wont exist yet (which trying to initialize/create the chromadb would cause fail/crash)
# (lazy singletons is a design pattern + timing behavior)
# (singleton = create something once and reuse it everywhere (like a database client, cache, or heavy object u dont want to recreate over and over))
# (lazy (in "lazy singleton") = dont create it until you actually need it)
# (so aka lazy singleton = created once, but only when needed)
# (the FastAPI startup event downloads chroma_db from S3 first. these init on the first actual request)
# we have to do this way because it's how Lambda initializes its environment (cold start)
# _get_rag_resources() initializes them on the first request (after the startup event has already downloaded /tmp/chroma_db). 
# llm stays module-level since it's just a Groq API client with no local file dependency.
_client = None
_collection = None
_embed_model = None

def _get_rag_resources():
    global _client, _collection, _embed_model
    if _client is None:
        # load chromaDB and embedding model 
        # initialize ChromaDB client 
        _client = chromadb.PersistentClient(
            path=os.getenv('CHROMA_PATH', '../../ragpipeline/data/chroma_db')
        )

        # loads chromadb collection(table) with dataset name i chose in embed.py (contains text chunks (documents), embeddings, metadata)  
        _collection = _client.get_collection('dog_care_articles')

        # load embedding model 
        # IMPORTANT: you must use the same model you used when storing embeddings!!!!!!!!
        _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _client, _collection, _embed_model

# Initialize Groq LLM for generating responses for user
llm = ChatGroq(
    model='llama-3.1-8b-instant', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)

# the final piece of the RAG pattern: retrieving relevant context, then generating an informed answer using the LLM
def retrieve_and_answer(question: str, breed: str):
    # we're not using client here, we just needed to initialize that, so we have _ in its place here
    _, collection, embed_model = _get_rag_resources()

    # 1. embed player's question
    # IMPORTANT: convert query -> embedding (that actually makes a lot of sense!! how else are we supposed to map and compare vectors)
    query_embedding = embed_model.encode([question]).tolist()

    # 2. find top 3 most similar chunks in ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3 #return top 3 matches
    )
    context_docs = results['documents'][0] #need [0] bc .query returns lists of lists. outer list is responses per query, inner list is the actual responses for individual queries
    context = '\n\n'.join(context_docs) #combines context_docs, which is a list[], into one string to pass into prompt. Choosing to separate each chunk with \n\n bc using a comma or period or single space etc wouldn't clearly show they are different chunks. helps LLM indicate these are separate chunks and treats each chunk independently instead of all one thought/piece of info

    metadatas = results['metadatas'][0]
    # deduplicate source URLs. multiple chunks might come from same article
    # dict.fromkeys() removes duplicates while preserving order
    sources = list(dict.fromkeys(
        m['source_url'] for m in metadatas
        if m.get('source_url')
    ))
    
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