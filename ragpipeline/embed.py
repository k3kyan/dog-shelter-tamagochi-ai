import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter


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
            raw_chunks.append({
                'text': chunk,
                'source_url': article['url'], 
                'full_article': article['text']  # keep for context generation for generate_context() for Groq (dont need to store permanently in chunk data or pass it to ChromaDB)
            })
    
    print(f"Total raw chunks: {len(raw_chunks)}")

    # looking at chunks to check and make sure theyre valid
    for chunk in raw_chunks[:3]:
        print(f"Checking random chunk: {chunk['filename']} \nChunk Len: ({len(chunk['text'])} chars)")
        print(chunk['text'][:100])

    return None


# 3. Contextrual Retrieval

# 4. Embed and store in ChromaDB


# 5. Run it all together
if __name__ == '__main__':
    import json, os
    articles = load_articles('../scraper/data/articles')
    chunk(articles)