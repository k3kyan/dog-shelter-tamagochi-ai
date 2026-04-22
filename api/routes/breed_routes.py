import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger
from services.etlpipeline_loader import breed_df

breed_router = APIRouter(
    prefix="/breeds",
    tags=["breeds"]
)

# breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# get list of breeds with shelter stats for the adoption screen
@breed_router.get("/")
def get_breeds():
    df = breed_df[['breed', 'avg_days_in_shelter']].copy()
    df['breed'] = df['breed'].str.title()
    return df.sort_values('breed').to_dict(orient='records')


# get specific breed info from pandas dataframe
@breed_router.get("/{breed_name}")
def get_breed(breed_name: str):
    row = breed_df[breed_df['breed'] == breed_name.upper()]
    if row.empty:
        raise HTTPException(status_code=404, detail='Breed not found')
    return row.iloc[0].to_dict()