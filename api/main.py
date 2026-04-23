# referenced my website project bc i've done this backend fastapi setup before
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from contextlib import asynccontextmanager
import os, boto3

from routes import breed_routes, player_routes, care_routes, agent_routes

# lambda startup code to download files from s3
# bc lambda filesystem is ephemeral (temporary) (on cold start / fresh run it starts empty, anything you write to lambda filesystem may disappear at any time, its only sometimes reused if the same container stays warm)
@asynccontextmanager
async def lifespan(app: FastAPI):
    bucket = os.getenv('DATA_BUCKET')
    if bucket:  # skip when running locally (DATA_BUCKET only set in Lambda env vars via template.yaml)
        s3 = boto3.client('s3')
        try:
            s3.download_file(bucket, 'breed_profiles.parquet', '/tmp/breed_profiles.parquet')
        except Exception as e:
            raise RuntimeError(f"Failed to download breed_profiles.parquet from S3 bucket '{bucket}': {e}") from e

        # need to download ChromaDB from S3 to /tmp
        # rag_chat_agent.py uses chromadb.PersistentClient(path=...) which needs a writable directory
        # Lambda's only writable path is /tmp. The Lambda container filesystem itself is read-only.
        # TODO:
        try:
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix='chroma_db/'):
                for obj in page.get('Contents', []):
                    local_path = f"/tmp/{obj['Key']}"
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    s3.download_file(bucket, obj['Key'], local_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download chroma_db from S3 bucket '{bucket}': {e}") from e
    # everything before yield = startup (runs once before first request)
    yield  # app runs here ("app is live, handle requests now"). anything after yield would be shutdown logic (not needed)
    # everything in the lifespan function after yield = shutdown (runs when app stops) (the below code is valid bc its connected to the "app" object directly)

# creates the app, registers lifespan
# when the app starts serving (Lambda cold start), FastAPI calls lifespan(app), runs the startup code, hits yield, then starts accepting requests
app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
    # insert cloudfront url here later
]
app.add_middleware(
    CORSMiddleware, 
    # allow_origins=origins, #if i only wanted to allow specific urls to access
    allow_origins=["*"],
    allow_methods=["*"], 
    allow_headers=["*"]
)


app.include_router(breed_routes.breed_router)
app.include_router(player_routes.player_router)
app.include_router(care_routes.care_router)
app.include_router(agent_routes.agent_router)


handler = Mangum(app)