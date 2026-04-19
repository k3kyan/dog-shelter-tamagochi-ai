import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import time # wait between calls to stay under the Groq limit (30 requests/minute on llama 3 8B)
import json
from sentence_transformers import SentenceTransformer
import chromadb
load_dotenv()

# Initialize Groq LLM for context generation
llm = ChatGroq(
    model='llama-3.1-8b-instant', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)

# 1. load article text files
def load_articles(dirpath: str) -> list[str]:
    """
    Load the article text files from the scraped data
    """
    ARTICLES_DIR = Path(os.getenv('ARTICLES_DIR', dirpath))
    articles = []

    for txt_file in sorted(ARTICLES_DIR.glob('*.txt')):
        with open(txt_file, encoding='utf-8') as f:
            content = f.read()
        
        # first line is SOURCE: url, rest is article text
        lines = content.split('\n\n', 1)
        source_url = lines[0].replace('SOURCE: ', '').strip()
        text = lines[1].strip() if len(lines) > 1 else ''
        if len(text) > 200:
            articles.append({
                'url': source_url,
                'text': text,
            })

    print(f"Loaded {len(articles)} articles from {ARTICLES_DIR}")
    return articles


# 2. Chunk with recursive character text splitter
# + generate context with groq to embed
# TODO-LATER: outputs the chunks list but prob a better way to do this
def chunk(articles: list[str]) -> list[str]:
    # Text splitter, since the articles are too long to embed whole. splitting into focused chunks means retrieval returns relevant pieces, not entire articles
    # RecursiveCharacterTextSplitter tries paragraph breaks first, then sentences, then words
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, #500 char is approx 80-100 words, 5 sentences is generally like 50-100 words, paragraphs generally have 4-7 sentences. Good size for small retrieval without whole article, large enough to maintain context
            chunk_overlap=80, #80 char is like 15-20 words ave, so prob enough for like a sentence overlap. 
            separators=['\n\n', '\n', '. ', ' ', ''],
    )

    # chunk all articles
    all_chunks = []
    article_no = 0
    last_time = time.perf_counter()
    for article in articles:
        chunks = splitter.split_text(article['text']) #splits the article's 'text' field into a list of chunks of 500 chars
        
        # Check: logging how long it takes between each processing
        print(f"Total chunks for article no. {article_no}: {len(chunks)}")
        article_no = article_no + 1
        chunk_no = 0

        for chunk in chunks: # add the chunks to all_chunks list, still keeping the other metadata for better context
            
            current_time = time.perf_counter()
            elapsed = current_time - last_time
            last_time = current_time
            print(f"Article no. {article_no} Chunk no. {chunk_no}: waited {elapsed:.2f} seconds")

            # generate context for each chunk
            context = generate_context(article['text'], chunk)
            
            # append chunks for embedding
            all_chunks.append({
                'chunk': chunk, #for embedding + stored as metadata in ChromaDB for debugging retrieval quality
                'context': context, #for embedding + stored as metadata in ChromaDB for debugging retrieval quality
                'source_url': article['url'] #stored as metadata for display
            })

            print(f"\nProcessed chunk: {chunk[:50]}")
            print(f"Processed context: {context[:50]}")
            # time.sleep(2)   # stay under Groq's 30 req/min rate limit
    
    print(f"Total contextualized chunks: {len(all_chunks)}")

    # Check: looking at chunks to check and make sure theyre valid
    for chunk in all_chunks[:3]:
        print(f"Checking random chunk: {chunk['filename']} \nChunk Len: ({len(chunk['text'])} chars)")
        print(chunk['text'][:100])

    # Store in json so when rerunning program, wont have to wait for Groq to regenerate the contexts per chunks again
    os.makedirs('data', exist_ok=True)
    with open('data/contextualized_chunks.json', 'w') as f:
        json.dump(all_chunks, f, indent=2)
    print("Saved contextualized_chunks.json")

    return all_chunks


# 3. Contextrual Retrieval (generated as each chunk is processed above)
def generate_context(full_article: str, chunk: str) -> str:
    """
    Takes full article (context) and a chunk from it
    Generates a short context sentence using Groq
    Returns a 1-2 sentence context description of the chunk
    """

    prompt = f"""You are helping build a RAG system for dog care information. Given this article excerpt and a specific chunk from it, write 1-2 sentences describing what the chunk is about and where it fits in the article.
    Be specific: mention the breed if relevant and the topic.
    Keep it under 100 words. Output ONLY the context sentence, nothing else.

    Article excerpt: {full_article[:2000]}

    Chunk to contextualize: {chunk}

    Context sentence:
    """
    # IMPORTANT!! {full_article[:2000]} truncate to avoid hitting Groq's tokens-per-minute limit, reduce token usage and stop rate limiting
    #the "Context sentence:" being left at the end of the prompt string is a prompting technique called a "completion prompt". Also prevents it from giving unecessary conversational text like "Sure! here u go" so u go straight to the content u want

    try:
        response = llm.invoke(prompt)
        context = response.content.strip() #in case theres whitespace before/after string, since llm's frequently return texts with trailing whitespace
        return context
    except Exception as e:
        print(f"Context generation failed: {e}")
        return ''
    

# 4. Embed chunks and store in ChromaDB
# THE CORE OF A RAG PIPELINE!!!!!!
def embed_in_chromadb(contextualized_chunks):

    # Load the sentence transformer embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2') #fast and free model, ~80MB, good general purpose quality (first run downloads the model (~80MB) — takes 1-2 minutes)

    # Set up ChromaDB persistent client
    # Note: PersistentClient saves the vector database to disk so you embed once and the db persists between python sessions
    CHROMA_DIR = os.getenv('CHROMA_DIR', 'data/chroma_db')
    os.makedirs(CHROMA_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(
        name='dog_care_articles',
        metadata={'hnsw:space': 'cosine'} # cosine similarity is standard choice for text embedding similarity
    )
    
    # if ChromaDB already has data, skip re-embedding to save api calls and time
    if collection.count() > 0:
        print(f"ChromaDB already has {collection.count()} chunks. Skipping embedding")
        print("Delete data/chroma_db/ to force re-embed")
    else:
        # --------------------- actual processing ----------------------

        # make a list of the sentences to embed (context + chunk)
        documents = []
        for c in contextualized_chunks:
            if c['context']:
                combined_chunk_context = f"{c['context']}\n\n{c['chunk']}"
            else:
                combined_chunk_context = c['chunk']
            documents.append(combined_chunk_context)

        # generate unique id's for each chunk (bc chromadb requires an ID for each document)
        ids = []
        for i in range(len(contextualized_chunks)):
            ids.append(f"chunk_{i}")

        # metadata for each chunk
        metadatas = []
        for c in contextualized_chunks:
            metadatas.append({
                'chunk': c['chunk'],
                'context': c['context'],
                'source_url': c['source_url'] 
            })

        # Note: batches to avoid memory issues with large collections of text. processing 50 chunks per batch is good with most machines
        # also prevents timeouts
        # also speeds up embedding API's (TODO-LATER:but i need to research more about this point)
        BATCH_SIZE = 50
        for i in range(0, len(documents), BATCH_SIZE):
            # sections in batches
            batch_docs = documents[i:i+BATCH_SIZE]
            batch_ids  = ids[i:i+BATCH_SIZE]
            batch_metadatas = metadatas[i:i+BATCH_SIZE]

            # generate embeddings (!!!!!) (converts text -> vectors (embeddings) yay!!) 
            embeddings = model.encode(batch_docs).tolist()

            # store in ChromaDB (aka add everything to the chromadb vector database) (allows semantic search!! yayay)
            collection.add(
                documents=batch_docs, #the context+chunks texts
                embeddings=embeddings, #the embedding vectors! yay!!
                ids=batch_ids,
                metadatas=batch_metadatas, #for retrieval
            )

            # print progress in terminal as program runs
            print(f"Embedded batch {i//BATCH_SIZE + 1} / "
                f"{(len(documents)-1)//BATCH_SIZE + 1}")
        
        print(f"\nChromaDB complete: {collection.count()} items stored in database")



# 5. Run it all together
if __name__ == '__main__':
    import json, os
    articles = load_articles('../scraper/data/articles')
    contextualized_chunks = chunk(articles) # TODO-LATER: Actually, wouldn't it be better instead of storing each article, just chunk each as they come in ??? (will do that later)
    embed_in_chromadb(contextualized_chunks)