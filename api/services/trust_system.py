# Trust system logic determines dog's personality reveal and their mood


# the actions you do with the dog increases/decreases your trust level
TRUST_GAINS = {
    'play': 6, 
    'walk': 5, 
    'feed': 7, 
    'groom': 3, 
    'talk': 5,
    'ignore': -1
}

# TODO-later: could probably put these stage names as enums
# determines what stage of trust the dog is in based on trust value
# stage of trust determines whether personality and name are revealed
# stage of trust also determines the dog's mood towards you
def get_trust_stage(trust: float) -> dict:
    if trust < 30:
        return {'stage':'withdrawn','personality_revealed':False,
                'name_revealed':False,'ascii_mood':'scared'}
    elif trust < 60:
        return {'stage':'cautious','personality_revealed':False,
                'name_revealed':True,'ascii_mood':'cautious'}
    elif trust < 85:
        return {'stage':'warming','personality_revealed':True,
                'name_revealed':True,'ascii_mood':'happy'}
    else:
        return {'stage':'thriving','personality_revealed':True,
                'name_revealed':True,'ascii_mood':'thriving'}

# friendlier dog breeds = easier to gain more trust
# uses data from DogTime b1 + b4 https://www.kaggle.com/datasets/mexwell/dog-breeds-dogtime-dataset (all data is ranged val 1-5)
# Score 5/5 → 1.3x (easier time), Score 3/5 → 1.0x (neutral), Score 1/5 → 0.7x (super distrusting)
def trust_multiplier(affectionate: int, stranger_friendly: int) -> float:
    avg = (affectionate + stranger_friendly) / 2
    multiplier = round(
        0.7 + (avg - 1) * (0.6 / 4), # min is 0.7x multiplier, ave-1 changes range to [0,4], range of change is 0.6 with each of the 4 values in [0,4] increasing by 0.15
        2 #round to 2 decimal places for visual better
    )
    return multiplier
