from pymongo import MongoClient
from config import Config

_mongo_client = None

def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        cfg = Config.MONGODB_CONFIG
        _mongo_client = MongoClient(
            host=cfg['host'],
            port=int(cfg.get('port', 27017)),
            username=cfg.get('username'),
            password=cfg.get('password')
        )
    return _mongo_client

def get_db():
    return get_mongo_client()[Config.MONGODB_CONFIG['database']]
