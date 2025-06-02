import yaml
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
DATA_PATH = os.path.join(BASE_DIR, "data")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "processed_data")

# Création des dossiers si nécessaire
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)

def load_config():
    """Charge le fichier YAML de configuration"""
    with open(CONFIG_PATH, "r") as file:
        return yaml.safe_load(file)

CONFIG = load_config()
