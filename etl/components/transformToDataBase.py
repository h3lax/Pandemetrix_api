import numpy as np
import pandas as pd
import os
from configETL import CONFIG, DATA_PATH, PROCESSED_DATA_PATH

def load_csv(file_name):
    """ Charge un fichier CSV """
    file_path = os.path.join(DATA_PATH, file_name)
    return pd.read_csv(file_path)

def apply_transformations(df: pd.DataFrame, transformations):
    """ Applique les transformations spécifiées dans le fichier YAML """
    
    # Sélection des colonnes à garder
    if "columns_to_keep" in transformations:
        df = df[transformations["columns_to_keep"]]
    
    # Renommage des colonnes
    if "rename_columns" in transformations:
        df = df.rename(columns=transformations["rename_columns"])

    df = df.dropna(subset=['nouveaux_cas', 'nouveaux_deces'], how='all')

    # Conversion des types de données
    if "data_types" in transformations:
        for col, dtype in transformations["data_types"].items():
            if dtype == "datetime":
                df.loc[:, col] = pd.to_datetime(df[col], errors='coerce')
            elif dtype == "int":
                df.loc[:, col] = df[col].fillna(0).astype(int)
            elif dtype == "float":
                df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')
            elif dtype == "str":
                df.loc[:, col] = df[col].astype(str)

    # Filtrage des données 
    df = df.loc[~((df['nouveaux_cas'] == 0) & (df['nouveaux_deces'] == 0))]
    df = df.loc[~((df['nouveaux_cas'] < 0) | (df['nouveaux_deces'] < 0))]

    # Suppression des doublons
    if transformations.get("remove_duplicates", False):
        df = df.drop_duplicates()

    # Suppression des valeurs manquantes
    if transformations.get("remove_na", False):
        df = df.dropna()

    return df

def transform_data(file_key):
    """ Transforme les données en utilisant la config YAML """
    if file_key not in CONFIG["datasets"]:
        raise ValueError(f"Configuration pour '{file_key}' non trouvée.")

    transformations = CONFIG["datasets"][file_key]
    
    # Chargement du fichier CSV
    df = load_csv(transformations["input_file"])
    
    # Application des transformations
    df = apply_transformations(df, transformations)
    
    # Sauvegarde du fichier transformé
    output_path = os.path.join(PROCESSED_DATA_PATH, transformations["output_file"])
    df.to_csv(output_path, index=False)
    
    print(f"Transformation terminée pour {file_key}. Fichier sauvegardé : {output_path}")