# Need to build docker file for ecr bc sentence-transformers and torch are too big for lambda zip
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
# gcc/g++ needed to compile packages like numpy that don't have pre-built wheels for this platform
RUN dnf install -y gcc gcc-c++ && pip install -r requirements.txt --no-cache-dir

# pre-download the embedding model so it's baked into the image (not downloaded on cold start)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY main.py .
COPY database/ database/
COPY models/ models/
COPY routes/ routes/
COPY schemas/ schemas/
COPY services/ services/

CMD ["main.handler"]
