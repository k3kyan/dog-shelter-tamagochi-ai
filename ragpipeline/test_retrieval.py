# Verify contextual retrieval works correctly 
# aka tests whether the embeddings + stored chunks can actually return relevant results
import chromadb, os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()

# initialize ChromaDB client
# creates a persistent database connection (this is where my embeddings are stored on disk)
client = chromadb.PersistentClient(
    path = os.getenv('CHROMA_DIR', 'data/chroma_db')
)

# loads chromadb collection(table) with dataset name i chose in embed.py (contains text chunks (documents), embeddings, metadata)
collection = client.get_collection('dog_care_articles')

# load embedding model
# IMPORTANT: you must use the same model you used when storing embeddings!!!!!!!!
model = SentenceTransformer('all-MiniLM-L6-v2')

print(f"ChromaDB has {collection.count()} chunks\n")

# queries to test whether the chromadb retrieves relevant chunks
TEST_QUERIES = [
    "how often should I brush my dog?",
    "what foods are dangerous for dogs?",
    "how much exercise does a Labrador need?",
    "signs that my dog is in pain",
    "how to train a stubborn dog",
    "what vaccinations does my dog need?",
    "how do I groom a Golden Retriever?",
    "what should I feed a high energy breed?",
]

# test retreivals for each question
for query in TEST_QUERIES:
    # IMPORTANT: convert query -> embedding (that actually makes a lot of sense!! how else are we supposed to map and compare vectors)
    embedding = model.encode([query]).tolist()

    # query the database (using a semantic search!)
    results = collection.query(
        query_embeddings=embedding,
        n_results=2 #return top 2 matches
    )
    # results['documents'][0] = list of top results
    # results['documents'][0][0] = first result

    # print the best match found for that query
    print(f"\nQuery: {query}")
    print(f"Top result: {results['documents'][0][0][:500]}...")
    print(f"Source: {results['metadatas'][0][0]['source_url']}")


# Questions to ask to see if my rag pipeline works well
# For each query: does the retrieved chunk feel semantically relevant?
# Verify context sentences are at the start of results (contextual retrieval!)
        # you should see "This chunk describes..." prepended to chunks 
# If results look unrelated: check your articles cover that topic