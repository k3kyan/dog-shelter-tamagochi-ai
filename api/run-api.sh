#!/bin/bash

# make scripts executable
# run on git bash terminal:
# chmod +x run-api.sh

# run script
# ./run-api.sh 

# to see swaggerUI
# http://localhost:8000/docs

source apivenv/Scripts/activate
echo "Running virtual environment..."

uvicorn main:app --reload
echo "Running uvicorn server..."