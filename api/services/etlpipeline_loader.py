import pandas as pd, os
from dotenv import load_dotenv
load_dotenv()

_breed_df = None

def get_breed_df():
    global _breed_df
    if _breed_df is None:
        _breed_df = pd.read_parquet(os.getenv('DATA_PATH'))
    return _breed_df
