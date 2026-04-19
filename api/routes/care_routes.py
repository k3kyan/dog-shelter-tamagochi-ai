import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger

from services.trust_system import TRUST_GAINS, trust_multiplier, get_trust_stage
from schemas.care_schema import (
    CareRequestSchema
)

care_router = APIRouter(
    prefix="/care",
    tags=["care", "trust_system"]
)

breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# how user's action affect's a dog's trust level based on the breed's personality
# used for updating/calculating trust
# payload incoming request data must be passing in json in format of CareRequestSchema
@care_router.post('/')
def perform_care(req: CareRequestSchema):
    # find the breed in the parquet (converts to uppercase to match stored format) #TODO:
    row = breed_df[breed_df['breed'] == req.breed.upper()]
    if row.empty:
        raise HTTPException(status_code=404, detail='Breed not found')
    
    # get personality traits
    # row['affectionate'] gets the column (returns a pandas Series) (kinda confusing namewise here)
    # .iloc[0] gives the value from the first row at position index 0 ("integer location")
    # pandas returns a dataframe, not a single value, so i have to extract the value manually
    aff = int(row['affectionate'].iloc[0])
    sf = int(row['stranger_friendly'].iloc[0])

    # calculate trust gain
    # base action value x personality friendliness multiplier
    gain = round(TRUST_GAINS.get(req.action, 2) * trust_multiplier(aff, sf), 1)

    # update trust score (caps at 100)
    new_trust = min(100.0, round(req.current_trust + gain, 1))


    return {'new_trust': new_trust,  #updated trust value
            'trust_gain': gain, #how much the trust increased
            'trust_stage': get_trust_stage(new_trust)}
