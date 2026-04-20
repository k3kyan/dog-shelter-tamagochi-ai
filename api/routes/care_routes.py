import pandas as pd, os
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.logger import logger

from services.trust_system import TRUST_GAINS, trust_multiplier, get_trust_stage
from services.player_service import get_player, update_player
from schemas.care_schema import (
    CareRequestSchema, 
    TickRequestSchema
)

care_router = APIRouter(
    prefix="/care",
    tags=["care", "trust_system"]
)

# how user's action affect's a dog's trust level based on the breed's personality
# used for updating/calculating trust
# payload incoming request data must be passing in json in format of CareRequestSchema
#  backend fetches + updates game state itself
@care_router.post('/')
def perform_care(req: CareRequestSchema):
    player = get_player(req.player_name)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')

    # calculate trust gain using breed's friendliness scores
    gain = round(
        TRUST_GAINS.get(req.action, 2) *
        trust_multiplier(
            player['affectionate'],
            player['stranger_friendly']
        ), 1
    )
    # TODO:
    new_trust = min(100.0, round(player['trust'] + gain, 1))

    # calculate stat changes per action
    stat_changes = {
        'feed':  {'hunger': -30.0},   # hunger is 0=full, 100=starving
        'walk':  {'energy': -15.0, 'happiness': 20.0},
        'groom': {'happiness': 15.0},
        'play':  {'happiness': 25.0, 'energy': -10.0},
        'talk':  {'happiness': 5.0},
    }.get(req.action, {})

    # apply stat changes with bounds (0-100)
    updates = {'trust': new_trust}
    for stat, delta in stat_changes.items():
        current = player.get(stat, 50.0)
        updates[stat] = max(0.0, min(100.0, current + delta))

    # save to DynamoDB and return updated state
    updated = update_player(req.player_name, updates)
    updated['trust_stage'] = get_trust_stage(new_trust)
    updated['trust_gain'] = gain
    return updated


# drains stats over time, called by frontend timer
@care_router.post('/tick')
def tick(req: TickRequestSchema):
    player = get_player(req.player_name)
    if not player:
        raise HTTPException(status_code=404, detail='Player not found')

    # drain rates computed from real breed data
    # AKC energy_level 0.2-1.0 × 8 = 1.6-8 pts per tick
    energy_drain = round(player['energy_level'] * 8, 1)

    # DogTime weight_gain_risk 1-5 ÷ 5 × 6 = 1.2-6 pts per tick
    hunger_gain  = round((player['weight_gain_risk'] / 5) * 6, 1)

    # base happiness decay
    happiness_drain = 2.0

    updates = {
        'energy':    max(0.0, player['energy'] - energy_drain),
        'hunger':    min(100.0, player['hunger'] + hunger_gain),
        'happiness': max(0.0, player['happiness'] - happiness_drain),
    }

    # trust penalty if stats are critically low at withdrawn stage
    trust_stage = get_trust_stage(player['trust'])['stage']
    if trust_stage == 'withdrawn':
        if any(updates[s] < 20 for s in updates):
            updates['trust'] = max(5.0, player['trust'] - 1.0)

    updated = update_player(req.player_name, updates)
    updated['trust_stage'] = get_trust_stage(updated['trust'])
    return updated
