# from components.cli import main

# if __name__ == "__main__":
#     main()

from components.extract import extract_csv
from components.transformToDataBase import transform_data
from components.loadToDataBase import load_data
from configETL import CONFIG

def run_etl():
    print

    print("🔄 Extraction et Transformation des fichiers...")
    for file_key in CONFIG["datasets"]:
        transform_data(file_key)

    # print("🔄 Chargement des données dans PostgreSQL...")
    # for file_key in CONFIG["files"]:
    #     load_data(file_key)

    print("✅ Pipeline terminé !")

if __name__ == "__main__":
    run_etl()
