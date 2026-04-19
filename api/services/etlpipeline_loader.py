import pandas as pd, os

breed_df = pd.read_parquet(os.getenv('DATA_PATH'))

# TODO: is this implementation ok? should i have like checks or a getter method instead?