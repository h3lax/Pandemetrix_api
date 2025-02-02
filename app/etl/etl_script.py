import pandas as pd
from sqlalchemy import create_engine

# Database connection
engine = create_engine('postgresql://raw_user:raw_password@localhost:5433/raw_db')

def load_csv_to_db(file_path):
    # Load CSV data
    df = pd.read_csv(file_path)

    # Transform data if needed
    # For example, you can rename columns, handle missing values, etc.

    # Load data into the staging table
    df.to_sql('raw_data', engine, if_exists='append', index=False)

if __name__ == "__main__":
    load_csv_to_db('../data/bronze/covid_19_clean_complete.csv')