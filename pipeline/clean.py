import pandas as pd, os, logging
logging.basicConfig(level=logging.INFO)

# -------------------------------- CLEANING DATA --------------------------------
# --- CLEANING AUSTIN SHELTER DATASET (bc its hardest and biggest) ---

# 1. Load and filter dogs only
austin = pd.read_csv('data/raw/aac_intakes_outcomes.csv')
dogs = (
        austin[
            austin['animal_type'] == 'Dog'
        ]
        .copy()
    ) # Filters the dataframe to keep only rows where animal_type == 'Dog' out of the "austin" array. "austin['animal_type'] == 'Dog'"" is a boolean mask to filter rows ("keep only rows in austin[] where condition is True"). Also we need .copy() so pandas doesnt return a view of the og dataframe instead of an actual object (SettingWithCopyWarning)
logging.info(f"Dogs num of rows: {dogs.shape[0]}")

# 2. Filter out bad time_in_shelter_days values (data errors (look in jupyter for inspo))
dogs = dogs[dogs['time_in_shelter_days'] >= 0].copy() 
# no need for maximum since dogs can stay for a long time

# 3. Normalize breed names
dogs['breed'] = dogs['breed'].str.upper().str.strip() # removes capitlization inconsistencies and leading/trailing whitespace
dogs['breed'] = dogs['breed'].str.replace(' MIX', '', regex=False) # lots of mixes, would mess up breed names
dogs['breed'] = dogs['breed'].str.split('/').str[0] # keep just the first breed name if its a mix, easier to categorize
dogs['breed'] = dogs['breed'].str.strip() # just in case theres more whitespace after those changes

# 4. Calculate avg_days_in_shelter per breed
shelter_stats = (
        dogs.groupby('breed')['time_in_shelter_days']
        .mean()
        .reset_index()
    )
# groupby: grouping the dataframe by breed, so all rows for each breed are collected together in their own group (IMPORTANT!!!)
# were calculating ave days in shelter so need the ['time_in_shelter_days'] column
# aggregation: (taking group of rows and reducing them to a single value) .mean() calculate mean/average of time_in_shelter for each breed
# .reset_index() returns the result back into a normal dataframe/rows instead of groups, AKA "breed" becomes regular column again
# formatting trick with parenthesis
shelter_stats.columns = ['breed', 'avg_days_in_shelter'] # changing column name bc its not time_in_shelter_days after being grouped and averaged
shelter_stats['avg_days_in_shelter'] = shelter_stats['avg_days_in_shelter'].round(0).astype(int) #nearest whole number


# 5. Calculate starting_trust from avg_days_in_shelter
# NOTE: longer shelter stay = more withdrawn dog = lower starting trust
max_days = shelter_stats['avg_days_in_shelter'].max() #get highest number of average days just so i have a scale for the trust bar
normalized_ave_days = shelter_stats['avg_days_in_shelter'] / max_days # Normalize avg_days to 0-1 range

max_starting_trust = 70 # max_starting_trust is 70 bc most dogs will be not 100% trusting on first meeting

shelter_stats['starting_trust'] = ((100 - (normalized_ave_days * max_starting_trust)) # shelter_stats['avg_days_in_shelter'] / max_days : gives value between 0 to 1, with 0 is shortest stay and 1 is longest
                                   .clip(5, max_starting_trust-5)
                                   .round(1) # round so not a ton of decimals
                                ) # add new column for breed's starting trust value
# calculates starting trust by getting value of ave trust into value from 0 to 1 to get a value from the range of max_starting_trust, then making it a portion of 100
# the higher the amount of days, the higher the withdrawn is, = -100 is val of starting trust 
# 100 is the 100% trust, so subtracting it by the other stuff gives u the starting trust value




# --- CLEANING AKC ---
# 1. Load and normalize breed names
# 2. Filter only necessary columns
# 3. Handle nulls

# --- CLEANING DOGTIME ---
# 1. Load and normalize breed names
# 2. Filter only necessary columns
# 3. Rename columns bc the columns here are awful
# 4. Handle nulls



# -------------------------------- JOINING DATASETS --------------------------------