OWD_covid_vaccinations = "https://catalog.ourworldindata.org/garden/covid/latest/vaccinations_global/vaccinations_global.csv"
import pandas as pd
import numpy as np

df_testing = pd.read_csv(OWD_covid_vaccinations)

def clean_vaccination_data(data: pd.DataFrame) -> pd.DataFrame:
    print("Début du nettoyage des données de vaccination...")

    # Nettoyage des noms de colonnes
    data.columns = (
        data.columns.str.replace(r'[^0-9a-zA-Z]+', '', regex=True)
        .str.lower()
        .str.strip()
    )

    print(f"Nombre Data : {data.shape}")

    # Cleaning de la colonne date
    try:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
    except Exception:
        print("Attention: Impossible de convertir la colonne 'date'")

    # Tri et suppression des doublons
    data = data.sort_values(by=['country', 'date'])
    data = data.drop_duplicates()

    # Colonnes numériques
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce') 
        neg_count = (data[col] < 0).sum()
        if neg_count > 0:
            print(f"{neg_count} valeurs négatives corrigées dans '{col}'")
            data.loc[data[col] < 0, col] = np.nan

    # Interpolation par pays
    for country in data['country'].unique():
        mask = data['country'] == country
        for col in numeric_cols:
            data.loc[mask, col] = data.loc[mask, col].interpolate(method='linear')

    # Remplissage des valeurs restantes
    for col in data.select_dtypes(include='number').columns:
        data[col] = data[col].fillna(0)

    for col in data.select_dtypes(include='object').columns:
        if col != 'country':
            data[col] = data[col].fillna('')

    # Valeurs aberrantes
    print("Traitement des valeurs aberrantes...")
    for col in numeric_cols:
        Q1 = data[col].quantile(0.25)
        Q3 = data[col].quantile(0.75)
        IQR = Q3 - Q1
        min_val = max(0, Q1 - 1.5 * IQR)
        max_val = Q3 + 1.5 * IQR

        outliers = ((data[col] < min_val) | (data[col] > max_val)).sum()
        if outliers > 0:
            print(f"{outliers} valeurs aberrantes corrigées dans '{col}'")
            data.loc[data[col] > max_val, col] = max_val
            data.loc[data[col] < min_val, col] = min_val

    # Colonnes dérivées temporelles
    if 'date' in data.columns and pd.api.types.is_datetime64_dtype(data['date']):
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        data['week'] = data['date'].dt.isocalendar().week
        print("Ajout des colonnes year, month, week")

    print(f"Forme finale des données: {data.shape}")
    print("Nettoyage terminé.")
    return data

#clean_vaccination_data(df_testing)