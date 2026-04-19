# dog-shelter-tamagochi-ai
creating a project to learn data engineering and ai

Python 3.11.5
Node.js v24.14.1


## Local Deployment Commands
Pipeline: cd pipeline && pipelinevenv\Scripts\activate

## Project Structure
pipeline/: data engineering, pandas
scraper/: data acquisition, just get articles for rag pipeline 
rag/: chunking, embedding, chromaDB
api/: will use chromadb from rag
frontend/: frontend

## Running the project
1. pipeline/run_pipeline.py             run etl pipeline
2. (optional) scraper/url_scraper.py    get urls to scrape
3. scraper/article_scraper.py           get article content text
4. ragpipeline/embed.py                 builds chromadb database 
                                        (turns articles into chunks, 
                                        converts chunks to embeddings, 
                                        stores embeddings to chromadb vector database)
5. 