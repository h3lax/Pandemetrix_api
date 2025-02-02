import pandas as pd

def transform_data(data):
    if isinstance(data, str):
        data = pd.read_csv(data)

    # Clean column names
    data.columns = data.columns.str.replace('[^0-9a-zA-Z]+', '_', regex=True).str.lower()

    print("Data transformation complete.")
    return data