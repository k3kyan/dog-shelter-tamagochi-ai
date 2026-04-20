# when player finishes adopter profile and picks a breed, initialize their game state in dynamodb

import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger
from services.etlpipeline_loader import breed_df
from services.player_service import get_player, save_player
from services.trust_system import get_trust_stage 
from services.etlpipeline_loader import breed_df

from schemas.player_schema import (
    AdopterProfileSchema,
    StartGameSchema,
    PlayerProfileSchema
)

player_router = APIRouter(
    prefix="/player",
    tags=["player", "adopter", "startgame", "start"]
)

# create new player in dynamodb
@player_router.post('/')
def start_game(req: StartGameSchema):
    # check if player name already taken
    if get_player(req.player_name):
        raise HTTPException(
            status_code=409,
            detail=f"Player name '{req.player_name}' already exists. "
                f"Choose a different name or continue your existing game."
        )

    # fetch breed profile
    row = breed_df[breed_df['breed'] == req.breed.upper()]
    if row.empty:
        raise HTTPException(status_code=404, detail='Breed not found')
    breed_data = row.iloc[0].to_dict()

    # build initial player game state
    player = PlayerProfileSchema(
        player_name=req.player_name,
        breed=req.breed.upper(),
        adopter_profile=req.adopter_profile,

        # game stats — all start at reasonable values
        hunger=70.0,
        happiness=70.0,
        energy=80.0,
        health=90.0,

        # trust initialized from real shelter data
        trust=float(breed_data.get('starting_trust', 30.0)),

        # breed data to show to player later
        avg_days_in_shelter=float(breed_data.get('avg_days_in_shelter', 0)),
        personality_type=breed_data.get('personality_type', ''),
        temperament=breed_data.get('temperament', ''),
        energy_level=float(breed_data.get('energy_level', 0.5)),
        trainability=float(breed_data.get('trainability', 0.5)),
        grooming_frequency=float(breed_data.get('grooming_frequency', 0.5)),
        weight_gain_risk=float(breed_data.get('weight_gain_risk', 3)),
        exercise_needs=float(breed_data.get('exercise_needs', 3)),
        affectionate=int(breed_data.get('affectionate', 3)),
        stranger_friendly=int(breed_data.get('stranger_friendly', 3)),
    )

    save_player(player.model_dump())

    # return full player info bc the frontend uses it to initialize its display with these info
    return player




# # adopter profile matching endpoint
# # purpose: match player lifestyle to DogTime columns for compatibility


# breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# calculates score of every dog breed (in DogTime Data) based on how well it matches a user's lifestyle
# creates a scoring table using a dataframe with all breeds
# compatibility score (0-100)
@player_router.post('/match')
def match_breeds(profile: AdopterProfileSchema):
    scores = pd.DataFrame()
    scores['breed'] = breed_df['breed'].str.title()

    # TODO:
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

# restore game state for previous players
@player_router.get('/{player_name}')
def get_player_state(player_name: str):
    player = get_player(player_name)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')
    result = player.model_dump()
    result['trust_stage'] = get_trust_stage(player.trust)
    return result
