import pandas as pd

def transform_data(data: pd.DataFrame):
    """Transforms raw data into a standardized format."""

    # Column name cleanup
    data.columns = (
        data.columns.str.replace(r'[^0-9a-zA-Z]+', '_', regex=True)
        .str.lower()
        .str.strip()
    )

    # Drop completely empty columns
    data = data.dropna(axis=1, how="all")

    # Fill missing values
    for col in data.select_dtypes(include=['number']).columns:
        data[col] = data[col].fillna(0)  

    for col in data.select_dtypes(include=['object']).columns:
        data[col] = data[col].fillna('')

    # Remove duplicate rows
    data = data.drop_duplicates()

    for col in data.columns:
         # Convert potential date columns
        if "date" in col or "timestamp" in col:
            try:
                data[col] = pd.to_datetime(data[col], errors='coerce')
                data[col] = data[col].fillna(pd.NaT)  # Ensure null values are explicit
            except Exception:
                print(f"Warning: Could not convert column '{col}' to datetime")

        # Convert text-based numeric columns to numbers
        if data[col].dtype == 'object':  
            if data[col].str.replace('.', '', 1).str.isnumeric().all():  # Check if all values are numbers
                try:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                except Exception:
                    print(f"Warning: Could not convert column '{col}' to numeric")

    print(" Data transformation complete.")
    return data
