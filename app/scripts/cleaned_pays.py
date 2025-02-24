import pandas as pd

# Charger vos DataFrames
cleaned_covid19 = pd.read_csv("cleaned_covid19.csv")
pays_info = pd.read_csv("pays.csv")

# Jointure sur la colonne commune, ici 'pays' (adapter selon vos vrais noms de colonnes)
cleaned_covid19_complet = pd.merge(
    pays_info,
    cleaned_covid19[['pays', 'region_oms']],  # ou toute autre colonne nécessaire
    on='pays',            # nom de la colonne commune
    how='left'            # équivalent d'un left_join
)

# La colonne 'region_oms' sera alors ajoutée à cleaned_covid19_complet
cleaned_covid19_complet.to_csv("cleaned_covid19_complet.csv", index=False)