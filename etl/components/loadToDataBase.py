import os
import pandas as pd
from MSPR.Pandemetrix_api.etl.configETL import PROCESSED_DATA_PATH
from app.db import db
from models import Continent, Pays, Rapport, Concerne  # À adapter selon vos noms de fichiers

def load_data(file_key, config):
    """
    Charge dans la base le CSV transformé (cleaned) correspondant à file_key.
    """
    # 1) Récupérer le chemin du CSV transformé
    load_config = config["datasets"][file_key]
    output_file = load_config["output_file"]  # ex: "cleaned_covid19.csv"
    csv_path = os.path.join(PROCESSED_DATA_PATH, output_file)

    # 2) Charger le CSV avec pandas
    df = pd.read_csv(csv_path)

    # 3) Parcourir le DataFrame et insérer / mettre à jour
    for _, row in df.iterrows():
        # Exemple: on récupère ou crée le continent
        continent_code = row.get("code_continent")  # selon vos colonnes
        if continent_code:
            continent = db.session.query(Continent).filter_by(code_continent=continent_code).first()
            if not continent:
                continent = Continent(code_continent=continent_code, nom="Nom par défaut")  # ou calculé
                db.session.add(continent)
        
        # Exemple: on récupère ou crée le pays
        pays_code = row.get("code_pays")
        if pays_code:
            pays = db.session.query(Pays).filter_by(code_pays=pays_code).first()
            if not pays:
                # On suppose qu'on a aussi la colonne "pays" pour le nom
                pays_nom = row.get("pays", "Pays inconnu")
                pays = Pays(code_pays=pays_code, nom=pays_nom, code_continent=continent_code)
                db.session.add(pays)
            else:
                # éventuellement on met à jour le nom...
                pass
        
        
        # Exemple: on crée le rapport
        # À adapter selon vos besoins et vos colonnes (nouveaux_cas, nouveaux_deces, etc.)
        rapport = Rapport(
            date_debut=row["date_debut"],
            date_fin=row["date_debut"],
            source="OMS",
            nouveaux_cas=row["nouveaux_cas"],
            nouveaux_deces=row["nouveaux_deces"],
            code_maladie=1,  # exemple: COVID-19
        )
        db.session.add(rapport)

        # Exemple: lier tout le monde via la table de jointure Concerne
        # On suppose qu'on a besoin de code_continent, code_pays, code_region, et l'id du rapport
        # ATTENTION: il faut db.session.flush() pour que rapport.id soit défini avant la création de Concerne
        db.session.flush()
        concerne = Concerne(
            code_continent=continent_code,
            code_pays=pays_code,
            code_rapport=rapport.id
        )
        db.session.add(concerne)

    # 4) Commit final après la boucle
    db.session.commit()
    print("Données insérées avec succès !")