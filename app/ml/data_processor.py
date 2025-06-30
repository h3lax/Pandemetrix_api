import pandas as pd
import os
from app.database.mongoClient import get_db
from typing import Dict, List, Optional

class MLDataProcessor:
    """Processeur de données pour ML intégré avec MongoDB"""
    
    def __init__(self):
        self.db = get_db()
    
    def check_csv_files_exist(self) -> Dict[str, bool]:
        """Vérifie si les fichiers CSV requis existent"""
        required_files = {
            "cases_deaths": "app/data/raw/cases_deaths.csv",
            "vaccinations": "app/data/raw/vaccinations_global.csv", 
            "hospital": "app/data/raw/hospital.csv",
            "testing": "app/data/raw/testing.csv"
        }
        
        status = {}
        for key, file_path in required_files.items():
            status[key] = {
                "path": file_path,
                "exists": os.path.exists(file_path),
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
        
        return status
    
    def load_csv_to_mongodb(self):
        """Charge les fichiers CSV dans MongoDB"""
        results = {}
        
        # Vérifier si les fichiers existent
        csv_files = {
            "cases_deaths": "app/data/raw/cases_deaths.csv",
            "vaccinations": "app/data/raw/vaccinations_global.csv", 
            "hospital": "app/data/raw/hospital.csv",
            "testing": "app/data/raw/testing.csv"
        }
        
        for key, path in csv_files.items():
            if not os.path.exists(path):
                results[key] = f"NOT FOUND: {path}"
                continue
                
            try:
                df = pd.read_csv(path)
                df = self._clean_dataframe(df)
                
                collection = self.db[f"ml_{key}"]
                collection.drop()
                
                if not df.empty:
                    records = df.to_dict('records')
                    collection.insert_many(records)
                    results[key] = f"SUCCESS: {len(records)} records"
                
            except Exception as e:
                results[key] = f"ERROR: {str(e)}"
        
        return results
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame"""
        # Standardiser les noms de colonnes
        df.columns = df.columns.str.lower().str.replace(r'[^a-z0-9_]', '_', regex=True)
        
        # Supprimer les colonnes complètement vides
        df = df.dropna(axis=1, how='all')
        
        # Standardiser la colonne date
        date_columns = [col for col in df.columns if 'date' in col]
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # Convertir en string pour MongoDB
                df[col] = df[col].dt.strftime('%Y-%m-%d')
            except:
                pass
        
        # Standardiser la colonne country/location
        country_columns = [col for col in df.columns if col in ['country', 'location', 'entity']]
        for col in country_columns:
            if col != 'country':
                df = df.rename(columns={col: 'country'})
        
        # Nettoyer les valeurs numériques
        numeric_columns = df.select_dtypes(include=['object']).columns
        for col in numeric_columns:
            if col not in ['country', 'date']:
                # Essayer de convertir en numérique
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remplir les valeurs manquantes
        for col in df.select_dtypes(include=['number']).columns:
            df[col] = df[col].fillna(0)
        
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna('')
        
        # Supprimer les lignes sans pays ou date
        if 'country' in df.columns:
            df = df[df['country'].str.strip() != '']
        if 'date' in df.columns:
            df = df[df['date'].notna()]
        
        return df
    
    def prepare_ml_dataset(self) -> str:
        """Prépare le dataset ML en fusionnant les collections MongoDB"""
        try:
            # Récupérer les données des collections
            cases_data = list(self.db.ml_cases_deaths.find())
            vaccinations_data = list(self.db.ml_vaccinations.find())
            hospital_data = list(self.db.ml_hospital.find())
            testing_data = list(self.db.ml_testing.find())
            
            if not cases_data:
                raise ValueError("No cases/deaths data found in MongoDB")
            
            # Convertir en DataFrames
            df_cases = pd.DataFrame(cases_data)
            df_vaccines = pd.DataFrame(vaccinations_data) if vaccinations_data else pd.DataFrame()
            df_hospital = pd.DataFrame(hospital_data) if hospital_data else pd.DataFrame()
            df_testing = pd.DataFrame(testing_data) if testing_data else pd.DataFrame()
            
            # Supprimer les _id MongoDB
            for df in [df_cases, df_vaccines, df_hospital, df_testing]:
                if '_id' in df.columns:
                    df.drop('_id', axis=1, inplace=True)
            
            # Fusion progressive sur country et date
            df_merge = df_cases.copy()
            
            # Standardiser les colonnes de jointure
            for df in [df_merge, df_vaccines, df_hospital, df_testing]:
                if not df.empty:
                    # S'assurer que les colonnes country et date existent
                    if 'country' not in df.columns:
                        # Chercher des alternatives
                        alt_country = [col for col in df.columns if 'location' in col or 'entity' in col]
                        if alt_country:
                            df.rename(columns={alt_country[0]: 'country'}, inplace=True)
                    
                    if 'date' not in df.columns:
                        alt_date = [col for col in df.columns if 'date' in col]
                        if alt_date:
                            df.rename(columns={alt_date[0]: 'date'}, inplace=True)
            
            # Fusion des données
            if not df_vaccines.empty and 'country' in df_vaccines.columns and 'date' in df_vaccines.columns:
                df_merge = pd.merge(df_merge, df_vaccines, on=['country', 'date'], how='left', suffixes=('', '_vax'))
            
            if not df_hospital.empty and 'country' in df_hospital.columns and 'date' in df_hospital.columns:
                df_merge = pd.merge(df_merge, df_hospital, on=['country', 'date'], how='left', suffixes=('', '_hosp'))
            
            if not df_testing.empty and 'country' in df_testing.columns and 'date' in df_testing.columns:
                df_merge = pd.merge(df_merge, df_testing, on=['country', 'date'], how='left', suffixes=('', '_test'))
            
            # Standardiser les noms des colonnes importantes
            column_mappings = {
                'new_cases': 'new_cases',
                'newcases': 'new_cases', 
                'cases': 'new_cases',
                'new_deaths': 'new_deaths',
                'newdeaths': 'new_deaths',
                'deaths': 'new_deaths',
                'people_vaccinated': 'people_vaccinated',
                'peoplevaccinated': 'people_vaccinated',
                'new_tests': 'new_tests',
                'newtests': 'new_tests',
                'daily_occupancy_hosp': 'daily_occupancy_hosp',
                'dailyoccupancyhosp': 'daily_occupancy_hosp',
                'hosp_patients': 'daily_occupancy_hosp',
                'hospital_patients': 'daily_occupancy_hosp'
            }
            
            for old_col, new_col in column_mappings.items():
                matching_cols = [col for col in df_merge.columns if old_col in col.lower()]
                if matching_cols and new_col not in df_merge.columns:
                    df_merge.rename(columns={matching_cols[0]: new_col}, inplace=True)
            
            # Nettoyer et filtrer
            df_merge = df_merge.dropna(subset=['country', 'date'])
            
            # Remplir les valeurs manquantes pour les colonnes importantes
            important_cols = ['new_cases', 'new_deaths', 'people_vaccinated', 'new_tests', 'daily_occupancy_hosp']
            for col in important_cols:
                if col in df_merge.columns:
                    df_merge[col] = pd.to_numeric(df_merge[col], errors='coerce').fillna(0)
            
            # Sauvegarder le dataset fusionné
            os.makedirs("data/processed", exist_ok=True)
            output_path = "data/processed/ml_merged_dataset.csv" 
            df_merge.to_csv(output_path, index=False)
            
            print(f"Dataset ML préparé: {len(df_merge)} lignes, {len(df_merge.columns)} colonnes")
            print(f"Colonnes disponibles: {list(df_merge.columns)}")
            print(f"Pays uniques: {df_merge['country'].nunique()}")
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Erreur préparation dataset ML: {str(e)}")
    
    def validate_ml_data_availability(self) -> Dict:
        """Vérifie la disponibilité des données pour ML depuis MongoDB"""
        collections = ['ml_cases_deaths', 'ml_vaccinations', 'ml_hospital', 'ml_testing']
        
        status = {}
        total_countries = set()
        
        for collection_name in collections:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                
                # Obtenir des échantillons
                sample_docs = list(collection.find().limit(3))
                columns = list(sample_docs[0].keys()) if sample_docs else []
                
                # Obtenir les pays uniques
                countries = collection.distinct('country') if count > 0 else []
                total_countries.update(countries)
                
                status[collection_name] = {
                    "exists": count > 0,
                    "rows": count,
                    "columns": [col for col in columns if col != '_id'],
                    "countries": len(countries),
                    "sample_countries": countries[:5]
                }
            except Exception as e:
                status[collection_name] = {
                    "exists": False,
                    "error": str(e)
                }
        
        # Vérifier les fichiers CSV
        csv_status = self.check_csv_files_exist()
        
        ready_for_training = any(info.get("exists", False) for info in status.values())
        
        return {
            "ready_for_training": ready_for_training,
            "mongodb_collections": status,
            "csv_files": csv_status,
            "total_unique_countries": len(total_countries),
            "countries_sample": list(total_countries)[:10],
            "recommendation": "Load CSV files to MongoDB first" if not ready_for_training else "Ready for ML training"
        }
    
    def get_country_data_sample(self, country: str = "France", limit: int = 10) -> Dict:
        """Récupère un échantillon de données pour un pays"""
        try:
            # Chercher dans les cases/deaths d'abord
            cases_data = list(self.db.ml_cases_deaths.find(
                {"country": {"$regex": country, "$options": "i"}}, 
                {"_id": 0}
            ).limit(limit))
            
            if not cases_data:
                # Essayer avec d'autres pays disponibles
                available_countries = self.db.ml_cases_deaths.distinct("country")[:5]
                return {
                    "country_requested": country,
                    "data_found": False,
                    "available_countries": available_countries,
                    "message": f"No data found for {country}. Try one of the available countries."
                }
            
            return {
                "country_requested": country,
                "data_found": True,
                "sample_data": cases_data,
                "total_records": self.db.ml_cases_deaths.count_documents({"country": {"$regex": country, "$options": "i"}})
            }
            
        except Exception as e:
            return {
                "country_requested": country,
                "data_found": False,
                "error": str(e)
            }