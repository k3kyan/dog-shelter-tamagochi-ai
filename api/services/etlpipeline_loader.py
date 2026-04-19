import pandas as pd, os

breed_df = pd.read_parquet(os.getenv('DATA_PATH'))