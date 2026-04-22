#!/bin/bash

# make scripts executable
# run on git bash terminal:
# chmod +x run-api.sh

# run script
# ./run-api.sh 


# --------------------------------- FastAPI

# to see swaggerUI
# http://localhost:8000/docs

source apivenv/Scripts/activate
echo "Running virtual environment..."

uvicorn main:app --reload
echo "Running uvicorn server..."

# --------------------------------- Docker DynamoDB

# # run setup_db.py yet if you havent, to set up dynamodb table

# # check docker running
# docker ps

# # start up 
# docker-compose up

# # shuts down container but preserves data
# docker-compose down 