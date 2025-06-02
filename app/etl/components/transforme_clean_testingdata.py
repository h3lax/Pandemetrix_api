import pandas as pd
import numpy as np

OWD_covid_testing = "https://catalog.ourworldindata.org/garden/covid/latest/testing/testing.csv"
df_testing = pd.read_csv(OWD_covid_testing)

# Fonction de nettoyage des données de testing
# Cette fonction prend un DataFrame en entrée et effectue plusieurs étapes de nettoyage, y compris la suppression des doublons, le traitement des valeurs manquantes et aberrantes, et l'interpolation des données.
def clean_testingdata(data: pd.DataFrame):

    print("Début du nettoyage des données de testing...")

    data.columns = (
    data.columns.str.replace(r'[^0-9a-zA-Z_]+', '', regex=True)  # Added _ to keep underscores
    .str.lower()
    .str.strip()
    )

    data = data.dropna(axis=1, how="all")

    print(f"Forme initiale des données: {data.shape}")

    try:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
    except Exception:
        print("Avertissement: Impossible de convertir la colonne 'date' en datetime")

    data = data.sort_values(by=['country', 'date'])

    doublons_avant = data.shape[0]
    data = data.drop_duplicates()
    doublons_supprimes = doublons_avant - data.shape[0]
    print(f"Doublons supprimés: {doublons_supprimes}")

    colonnes_numeriques = [
        'total_tests', 'new_tests', 'total_tests_per_thousand', 'new_tests_per_thousand', 'new_tests_7day_smoothed', 'new_tests_per_thousand_7day_smoothed'     
    ]

    for col in colonnes_numeriques:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            negatifs_count = (data[col] < 0).sum()
            if negatifs_count > 0:
                print(f"Correction de {negatifs_count} valeurs négatives dans '{col}'")
                # Cette ligne remplace les valeurs négatives par des valeurs manquantes (NaN) dans une colonne spécifique.
                data.loc[data[col] < 0, col] = np.nan

    pays_count = data['country'].nunique()
    print(f"Interpolation des valeurs pour {pays_count} pays... ")

    # Cette section de code effectue l'interpolation linéaire des valeurs manquantes, pays par pays.
    # Exemple: si un pays a des valeurs [100, NaN, NaN, 400] sur 4 jours consécutifs, l'interpolation estimera les valeurs manquantes comme [100, 200, 300, 400]

    for pays in data['country'].unique():
        mask = data['country'] == pays
        for col in colonnes_numeriques:
            if col in data.columns:
                data.loc[mask, col] = data.loc[mask, col].interpolate(method='linear')

    na_count_before = data[colonnes_numeriques].isna().sum().sum()

    for col in data.select_dtypes(include=['number']).columns:
        data[col] = data[col].fillna(0)

    for col in data.select_dtypes(include=['object']).columns:
        if col != 'country':
            data[col] = data[col].fillna('')

    na_count_after = data[colonnes_numeriques].isna().sum().sum()
    print(f"Valeurs manquantes remplies: {na_count_before - na_count_after}")

    print("Traitement des valeurs aberrantes...")
    for col in colonnes_numeriques:
        if col in data.columns:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1

            limite_inf = max(0, Q1 - 1.5 * IQR)
            limite_sup = Q3 + 1.5 * IQR

            outliers_count = ((data[col] > limite_sup) | (data[col] < limite_inf)).sum()
            if outliers_count > 0:
                print(f"Correction de {outliers_count} valeurs aberrantes dans '{col}'")

                data.loc[data[col] > limite_sup, col] = limite_sup
                data.loc[data[col] < limite_inf, col] = limite_inf

    if 'date' in data.columns and pd.api.types.is_datetime64_dtype(data['date']):
        data['year'] = data['date'].dt.year
        data['month'] = data['date'].dt.month
        data['week'] = data['date'].dt.isocalendar().week
        print("Colonnes temporelles dérivées ajoutées (year, month, week)")
    
    if 'total_tests' in data.columns and 'new_tests' in data.columns:
        inconsistent_rows = (data['total_tests'] < data['new_tests']).sum()
        if inconsistent_rows > 0:
            print(f"Correction de {inconsistent_rows} incohérences entre total_tests et new_tests")
            # Dans ces cas, ajustons total_tests pour qu'il soit au moins égal à new_tests
            data.loc[data['total_tests'] < data['new_tests'], 'total_tests'] = \
                data.loc[data['total_tests'] < data['new_tests'], 'new_tests']
    
    print(f"Forme finale des données: {data.shape}")
    print("Nettoyage des données terminé.")
    return data

#clean_testingdata(df_testing)