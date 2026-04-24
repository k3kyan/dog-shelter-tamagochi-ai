# Need to build docker file for ecr bc sentence-transformers and torch are too big for lambda zip
# JK i'm replacing sentence-transformers and torch with HuggingFace api but still keeping docker file for the other dependencies which are too big for lambda zip
FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY main.py .
COPY database/ database/
COPY models/ models/
COPY routes/ routes/
COPY schemas/ schemas/
COPY services/ services/
RUN echo "Files in /var/task:" && ls /var/task/

CMD ["main.handler"]
