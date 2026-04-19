import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger
from services.etlpipeline_loader import breed_df

breed_router = APIRouter(
    prefix="/breeds",
    tags=["breeds"]
)

# breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# get list of breeds
@breed_router.get("/")
def get_breeds():
    return sorted(breed_df['breed'].str.title().tolist())


# get specific breed info from pandas dataframe
@breed_router.get("/{breed_name}")
def get_breed(breed_name: str):
    row = breed_df[breed_df['breed'] == breed_name.upper()]
    if row.empty:
        raise HTTPException(status_code=404, detail='Breed not found')
    return row.iloc[0].to_dict()