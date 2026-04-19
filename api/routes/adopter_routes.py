# adopter profile matching endpoint
# purpose: match player lifestyle to DogTime columns for compatibility
import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger
from services.etlpipeline_loader import breed_df

from schemas.adopter_schema import (
    AdopterProfileSchema
)

adopter_router = APIRouter(
    prefix="/adopter",
    tags=["adopter"]
)

# breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# calculates score of every dog breed (in DogTime Data) based on how well it matches a user's lifestyle
# creates a scoring table using a dataframe with all breeds
# compatibility score (0-100)
@adopter_router.post('/match')
def match_breeds(profile: AdopterProfileSchema):
    scores = pd.DataFrame()
    scores['breed'] = breed_df['breed'].str.title()

    # 1. apartment: DogTime a1 (1-5, higher = better for apartment)
    scores['living'] = breed_df['apartment_friendly'] \
        if profile.living_situation == 'apartment' else 5

    # 2. climate: DogTime a5 (cold) or a6 (hot)
    if profile.climate == 'hot':
        scores['climate'] = breed_df['tolerates_hot']
    elif profile.climate == 'cold':
        scores['climate'] = breed_df['tolerates_cold']
    else:
        scores['climate'] = 5

    # 3. time home: DogTime a4 (tolerates_alone)
    if profile.time_home == 'rarely':
        scores['alone'] = breed_df['tolerates_alone']
    elif profile.time_home == 'sometimes':
        scores['alone'] = breed_df['tolerates_alone'].clip(lower=3)
    else:
        scores['alone'] = 5

    # 4. experience: DogTime a2
    scores['experience'] = breed_df['novice_owner_friendly'] \
        if profile.experience == 'first_time' else 5

    # overall: avg of 4 scores scaled to 0-100
    scores['compatibility'] = (
        (scores['living'] + scores['climate'] +
        scores['alone'] + scores['experience']) / 20 * 100
    ).round(0).astype(int)

    return scores.set_index('breed')['compatibility'].to_dict()
