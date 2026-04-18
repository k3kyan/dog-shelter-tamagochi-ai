import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
import time # wait between calls to stay under the Groq limit (30 requests/minute on llama 3 8B)

# Initialize Groq LLM for context generation
llm = ChatGroq(
    model='llama3-8b-8192', #fast and free model, context generation is simple so dont need large model
    api_key=os.getenv('GROQ_API_KEY'),
)

# 1. load article text files
def load_articles(dirpath: str) -> list[str]:
    """
    Load the article text files from the scraped data
    """
    load_dotenv()
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





# TODO: Actually, wouldn't it be better instead of storing each article, just chunk each as they come in ???


# 2. Chunk with recursive character text splitter
# + generate context with groq to embed
def chunk(articles: list[str]):
    # Text splitter, since the articles are too long to embed whole. splitting into focused chunks means retrieval returns relevant pieces, not entire articles
    # RecursiveCharacterTextSplitter tries paragraph breaks first, then sentences, then words
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, #500 char is approx 80-100 words, 5 sentences is generally like 50-100 words, paragraphs generally have 4-7 sentences. Good size for small retrieval without whole article, large enough to maintain context
            chunk_overlap=80, #80 char is like 15-20 words ave, so prob enough for like a sentence overlap. 
            separators=['\n\n', '\n', '. ', ' ', ''],
    )

    # chunk all articles
    raw_chunks = []
    for article in articles:
        chunks = splitter.split_text(article['text']) #splits the article's 'text' field into a list of chunks of 500 chars
        for chunk in chunks: # add the chunks to raw_chunks list, still keeping the other metadata for better context
            
            # generate context for each chunk
            context = generate_context(article['text'], chunk)
            
            # append chunks for embedding
            raw_chunks.append({
                'chunk': chunk, #for embedding + stored as metadata in ChromaDB for debugging retrieval quality
                'context': context, #for embedding + stored as metadata in ChromaDB for debugging retrieval quality
                'source_url': article['url'] #stored as metadata for display
            })

            time.sleep(2)   # stay under Groq's 30 req/min rate limit
    
    print(f"Total raw chunks: {len(raw_chunks)}")

    # Check: looking at chunks to check and make sure theyre valid
    for chunk in raw_chunks[:3]:
        print(f"Checking random chunk: {chunk['filename']} \nChunk Len: ({len(chunk['text'])} chars)")
        print(chunk['text'][:100])

    # TODO: Store in json so when rerunning program, wont have to wait for Groq to regenerate the contexts per chunks again

    return None



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

    Full Article: {full_article}

    Chunk to contextualize: {chunk}

    Context sentence:
    """
    #the "Context sentence:" being left at the end of the prompt string is a prompting technique called a "completion prompt". Also prevents it from giving unecessary conversational text like "Sure! here u go" so u go straight to the content u want

    try:
        response = llm.invoke(prompt)
        context = response.content.strip() #in case theres whitespace before/after string, since llm's frequently return texts with trailing whitespace
        return context
    except Exception as e:
        print(f"Context generation failed: {e}")
        return ''
    

# 4. Embed and store in ChromaDB


# 5. Run it all together
if __name__ == '__main__':
    import json, os
    articles = load_articles('../scraper/data/articles')
    chunk(articles)