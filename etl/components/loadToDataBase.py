import sys
import os
import pandas as pd
from sqlalchemy.orm import Session
from db import engine, SessionLocal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.models import Rapport, Pays, Maladie, Periode
import os
from configETL import CONFIG, PROCESSED_DATA_PATH



def get_code_maladie(nom_maladie):
    """Récupère le code de la maladie dans PostgreSQL"""
    session = SessionLocal()
    code = session.query(Maladie.code_maladie).filter(Maladie.nom == nom_maladie).scalar()
    session.close()
    return code

def get_code_periode(date):
    """Récupère le code période correspondant à l'année de la date"""
    session = SessionLocal()
    code = session.query(Periode.code_periode).filter(Periode.nom == str(date.year)).scalar()
    session.close()
    return code

def get_code_pays(code_pays):
    """Vérifie si le pays existe dans la base"""
    session = SessionLocal()
    exists = session.query(Pays.code_pays).filter(Pays.code_pays == code_pays).scalar()
    session.close()
    return exists is not None

def load_data(file_key):
    """Charge les données d'un fichier CSV spécifique dans PostgreSQL"""
    if file_key not in CONFIG["files"]:
        print(f"⚠️ Aucune configuration trouvée pour '{file_key}'")
        return

    config = CONFIG["files"][file_key]
    file_path = os.path.join(PROCESSED_DATA_PATH, config["input_file"])

    if not os.path.exists(file_path):
        print(f"❌ Fichier non trouvé : {file_path}")
        return

    print(f"📥 Chargement des données depuis {file_path}...")
    df = pd.read_csv(file_path)

    # Récupérer la maladie associée
    nom_maladie = config["maladie"]
    code_maladie = get_code_maladie(nom_maladie)

    if not code_maladie:
        print(f"❌ Maladie inconnue dans la base : {nom_maladie}")
        return

    session = SessionLocal()

    try:
        for _, row in df.iterrows():
            # Vérification des clés étrangères
            code_periode = get_code_periode(row["date_debut"])
            
            if not code_periode or not get_code_pays(row["code_pays"]):
                print(f"⚠️ Données ignorées : {row}")
                continue

            rapport = Rapport(
                date_debut=row["date_debut"],
                date_fin=row["date_debut"],  # Supposition, peut être modifié
                source="OMS",
                nouveaux_cas=row["nouveaux_cas"],
                nouveaux_deces=row["nouveaux_deces"],
                nouveaux_gueris=row["nouveaux_gueris"],
                cas_actifs=row["cas_actifs"],
                taux_mortalite=row["taux_mortalite"],
                taux_guerison=row["taux_guerison"],
                code_maladie=code_maladie,
                code_periode=code_periode
            )

            session.add(rapport)

        session.commit()
        print(f"✅ Données de {nom_maladie} insérées dans PostgreSQL")

    except Exception as e:
        session.rollback()
        print(f"❌ Erreur lors de l'insertion des données {nom_maladie} : {e}")

    finally:
        session.close()
