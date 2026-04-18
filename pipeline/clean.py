import pandas as pd, os, logging
from thefuzz import process # add fuzzy merge function
logging.basicConfig(level=logging.INFO)

# -------------------------------- CLEANING DATA --------------------------------
# --- CLEANING AUSTIN SHELTER DATASET (bc its hardest and biggest) ---

# 1. Load and filter dogs only
# USE: time_in_shelter_days pre-calculated → avg per breed → starting_trust
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

logging.info(f"normalized_ave_days: {normalized_ave_days} days")
logging.info(f"normalized_ave_days.max(): {normalized_ave_days.max()} days")
logging.info(f"max_days.max(): {max_days.max()} days")

max_starting_trust = 70 # max_starting_trust is 70 bc most dogs will be not 100% trusting on first meeting

# TODO: ok this math is wrong but ig thats a later problem idk, the logs look right
shelter_stats['starting_trust'] = ((max_starting_trust - (normalized_ave_days * (max_starting_trust - 10))) # shelter_stats['avg_days_in_shelter'] / max_days : gives value between 0 to 1, with 0 is shortest stay and 1 is longest
                                   .round(1) # round so not a ton of decimals
                                ) # add new column for breed's starting trust value

logging.info(f"starting_trust: {(normalized_ave_days * (max_starting_trust-5))} trust")
logging.info(f"starting_trust: {shelter_stats['starting_trust']} trust")
# calculates starting trust by getting value of ave trust into value from 0 to 1 to get a value from the range of max_starting_trust, then making it a portion of 100
# the higher the amount of days, the higher the withdrawn is, = -100 is val of starting trust 
# 100 is the 100% trust, so subtracting it by the other stuff gives u the starting trust value




# --- CLEANING AKC ---
# USE: energy, trainability, demeanor, grooming, shedding scores --> KMeans clustering + LangChain trust-aware prompts

# 1. Load and normalize breed names
akc = pd.read_csv('data/raw/akc-dog-breeds.csv', index_col=0) #have to load index column 0 bc breed column doesnt have a name for some reason??
akc.index.name = 'breed' # the first column we set as index with index_col=0, we are renaming it to "breed"
akc = akc.reset_index() #turns index from breed(index) to just breed (bc it was weird before) aka a regular column and not an index (easier for merging/joining datasets later)
akc['breed'] = akc['breed'].str.upper().str.strip() # normalize breed names in case of irregular capitalization and leading/trailing whitespace

# 2. Filter only necessary columns
akc = akc[[
    'breed',
    'description',
    'temperament',
    'group',
    'min_expectancy',
    'max_expectancy',
    'grooming_frequency_value',
    'shedding_value',
    'energy_level_value',
    'trainability_value',
    'demeanor_value']]


# 3. Handle nulls 
akc = akc.dropna(subset=[
    'energy_level_value',
    'trainability_value',
    'demeanor_value',
    'grooming_frequency_value',
    'min_expectancy',
    'max_expectancy',
    'shedding_value']) #drops any rows(breeds) that are missing any of these columns (bc these columns are important)
                    # need to drop bc any null values will mess with calculations or ML models (which i'll do later). i drop these since these are VALUES
                    # .dropna() instead of .drop() bc .dropna() removes NaN's where .drop() would remove specific strings
akc['description'] = akc['description'].fillna('') # fill missing descriptions with empty strings, since these texts are not used in calculations but also shouldnt be null/NaN, so no string operations failing
akc['temperament'] = akc['temperament'].fillna('') 



# --- CLEANING DOGTIME ---
# USE: adopter profile matching (a1-a6) + trust multiplier (b1, b4) + game mechanic drain rates (c1-c5, d5, e1, e3, e4)

# 1. Load and normalize breed names
dogtime = pd.read_csv('data/raw/dogtime-dataset.csv')
dogtime['breed'] = dogtime['breed'].str.upper().str.strip() #normalize

# 2. Filter only necessary columns
dogtime = dogtime.drop(columns=['url']) #drop url column
dogtime = dogtime[[
          'breed',
          # adopter profile matching (lowkey will i use all of these?? kinda overcomplicated.. good for resume ig maybe..?)
          'a1_adapts_well_to_apartment_living',
          'a2_good_for_novice_owners',
          'a3_sensitivity_level',
          'a4_tolerates_being_alone',
          'a5_tolerates_cold_weather',
          'a6_tolerates_hot_weather',
          # trust multiplier
          'b1_affectionate_with_family',
          'b4_friendly_toward_strangers',
          # game mechanics
          'c1_amount_of_shedding',
          'c2_drooling_potential',
          'c3_easy_to_groom',
          'c4_general_health',
          'c5_potential_for_weight_gain',
          'd5_tendency_to_bark_or_howl',
          'e1_energy_level',
          'e3_exercise_needs',
          'e4_potential_for_playfulness',
      ]]


# 3. Rename columns bc the columns here are awful
dogtime = dogtime.rename(columns={
          'a1_adapts_well_to_apartment_living': 'apartment_friendly',
          'a2_good_for_novice_owners':          'novice_owner_friendly',
          'a3_sensitivity_level':               'sensitivity',
          'a4_tolerates_being_alone':           'tolerates_alone',
          'a5_tolerates_cold_weather':          'tolerates_cold',
          'a6_tolerates_hot_weather':           'tolerates_hot',
          'b1_affectionate_with_family':        'affectionate',
          'b4_friendly_toward_strangers':       'stranger_friendly',
          'c1_amount_of_shedding':              'shedding_dt',
          'c2_drooling_potential':              'drooling',
          'c3_easy_to_groom':                   'grooming_ease',
          'c4_general_health':                  'general_health',
          'c5_potential_for_weight_gain':       'weight_gain_risk',
          'd5_tendency_to_bark_or_howl':        'bark_tendency',
          'e1_energy_level':                    'energy_level_dt',
          'e3_exercise_needs':                  'exercise_needs',
          'e4_potential_for_playfulness':       'playfulness',
      })


# 4. Handle nulls
dogtime.isnull().sum()
dogtime = dogtime.dropna()

# -------------------------------- JOINING DATASETS --------------------------------
# Fuzzy-join all 3 cleaned datasets into one breed profile

def fuzzy_merge(df_a, df_b, columntomerge, threshold=80): 
    """
    Joins two datasets/dataframes on a string (columnname) using fuzzy matching (instead of exact string matching).
    threshold=80 means 80% string similarity required to match. (so matches columnname and merges even when the key strings dont match exactly)
    """
    # hold the best match for each row in df_a
    matches = []
    
    # for every string in the key columntomerge of df_a, find the closest match in df_b (there should only be one match since we cleaned the data)
    # loop through each "breed" value in df_a
    # match rows based on a string column (key)
    for breed in df_a[columntomerge]:
        result = process.extractOne(breed, df_b[columntomerge].tolist()) # find the closest match in df_b # use fuzzy string matching instead of exact equality # compares columnname (breed) to all values in df_b[breed] #returns (best_match, similarity_score) ex: ("Golden Retriver", 92)
        if result and result[1] >= threshold: # only keep matches with similarity ≥ threshold(which is 80)
            matches.append(result[0])
        else:
            matches.append(None)
    
    # add matches (the fuzzy match results) as a new column
    # bc there needs to be a JOIN KEY in the dataframe before it can merge (these values would be values from df_b[breed] column that most match the df_a[breed] column string)
    df_a = df_a.copy()
    df_a['matched_breed'] = matches
    
    # merge the dataframes
    # joins df_a['matched_breed'] with df_b[columntomerge]
    # how='inner' means (1) only rows with valid matches are kept (2) rows with None are dropped
    merged = df_a.merge(
        df_b, left_on='matched_breed', right_on=columntomerge, how='inner'
    )
    
    # clean up pandas anti collision renaming stuff + remove the join column since that was just for joining
    merged = merged.drop(columns=['matched_breed','breed_y'])
    merged = merged.rename(columns={'breed_x': 'breed'})

    return merged
# things about this method to improve eventually later
    # nested comparisons is slow for large datasets (leetcode!)
    # one sided matching, not symmetric, only matches df_a -> df_b

# join akc + dogtime first
akcdogtime = fuzzy_merge(akc, dogtime, 'breed')
logging.info(f"akc + dogtime datasets fuzzy merge: {akcdogtime.shape[0]} breeds matched")
# # clean up pandas anti collision renaming stuff + remove the join column since that was just for joining
# akcdogtime = akcdogtime.drop(columns=['matched_breed','breed_y'])
# akcdogtime = akcdogtime.rename(columns={'breed_x': 'breed'})

# Join Austin shelter stats
final = fuzzy_merge(akcdogtime, shelter_stats, 'breed')
logging.info(f"join austin dataset fuzzy merge: {final.shape[0]} breeds")
# # clean up pandas anti collision renaming stuff + remove the join column since that was just for joining
# final = final.drop(columns=['matched_breed','breed_y'])
# final = final.rename(columns={'breed_x': 'breed'})

# checking values that i merged correctly
logging.info(f"num of rows(breeds) and columns(traits): {final.shape}")
logging.info(f"names of columns: {final.columns.tolist()}")
logging.info(f"make sure no null/NaN: {final.isnull().sum()} = 0")
logging.info(f"make sure no duplicates: {final.duplicated(subset=['breed']).sum()} = 0") #expected: 0

# check specific example (golden retriever)
cols = [
    'breed',
    'energy_level_value',
    'trainability_value',
    'demeanor_value',
    'avg_days_in_shelter',
    'starting_trust',
    'apartment_friendly'
    ]
golden = final[final['breed'].str.contains('GOLDEN')][cols].T #transpose for readability, it was not well fitted for terminal before
logging.info(f"checking golden retriever profile: {golden}")


# Save intermediate file
os.makedirs('data/processed', exist_ok=True)
final.to_parquet('data/processed/breed_profiles.parquet', index=False)