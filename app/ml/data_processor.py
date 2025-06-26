import pandas as pd
from app.database.mongoClient import get_db
from typing import Dict, List, Optional

class MLDataProcessor:
    """Processeur de données pour ML intégré avec MongoDB"""
    
    def __init__(self):
        self.db = get_db()
    
    def export_covid_data_for_ml(self, collection_name: str = "covid_data_oms") -> str:
        """Exporte les données COVID depuis MongoDB vers CSV pour ML"""
        try:
            # Récupérer toutes les données
            data = list(self.db[collection_name].find())
            
            if not data:
                raise ValueError(f"Aucune donnée trouvée dans {collection_name}")
            
            df = pd.DataFrame(data)
            
            # Mapping des colonnes MongoDB vers format ML
            column_mapping = {
                'date_reported': 'date',
                'country': 'country',
                'new_cases': 'new_cases',
                'new_deaths': 'new_deaths',
                'cumulative_cases': 'total_cases',
                'cumulative_deaths': 'total_deaths'
            }
            
            # Renommer colonnes si elles existent
            existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_mapping)
            
            # Nettoyage des données
            df = self._clean_data(df)
            
            # Sauvegarder
            output_path = "data/raw/cases_deaths.csv"
            df.to_csv(output_path, index=False)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Erreur export données ML: {str(e)}")
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données pour ML"""
        # Supprimer colonnes MongoDB internes
        if '_id' in df.columns:
            df = df.drop('_id', axis=1)
        
        # Convertir date
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Nettoyer valeurs numériques
        numeric_cols = ['new_cases', 'new_deaths', 'total_cases', 'total_deaths']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Supprimer lignes avec dates invalides
        if 'date' in df.columns:
            df = df.dropna(subset=['date'])
        
        return df
    
    def create_synthetic_ml_data(self) -> Dict[str, str]:
        """Crée des données synthétiques pour ML (développement)"""
        import numpy as np
        from datetime import datetime, timedelta
        
        # Pays de test
        countries = ["France", "Germany", "Italy", "Spain", "United Kingdom"]
        
        # Générer dates
        start_date = datetime(2022, 1, 1)
        dates = [start_date + timedelta(days=i) for i in range(365)]
        
        data_sets = {}
        
        # 1. Cases and Deaths
        cases_deaths = []
        for country in countries:
            for date in dates:
                cases_deaths.append({
                    'country': country,
                    'date': date.strftime('%Y-%m-%d'),
                    'new_cases': np.random.poisson(1000),
                    'new_deaths': np.random.poisson(20),
                    'total_cases': np.random.randint(100000, 1000000),
                    'total_deaths': np.random.randint(1000, 50000)
                })
        
        cases_deaths_df = pd.DataFrame(cases_deaths)
        cases_deaths_path = "data/raw/cases_deaths.csv"
        cases_deaths_df.to_csv(cases_deaths_path, index=False)
        data_sets['cases_deaths'] = cases_deaths_path
        
        # 2. Vaccinations
        vaccinations = []
        for country in countries:
            for date in dates:
                vaccinations.append({
                    'country': country,
                    'date': date.strftime('%Y-%m-%d'),
                    'people_vaccinated': np.random.randint(10000000, 50000000),
                    'people_fully_vaccinated': np.random.randint(8000000, 45000000)
                })
        
        vaccinations_df = pd.DataFrame(vaccinations)
        vaccinations_path = "data/raw/vaccinations_global.csv"
        vaccinations_df.to_csv(vaccinations_path, index=False)
        data_sets['vaccinations'] = vaccinations_path
        
        # 3. Hospital
        hospital = []
        for country in countries:
            for date in dates:
                hospital.append({
                    'country': country,
                    'date': date.strftime('%Y-%m-%d'),
                    'daily_occupancy_hosp': np.random.randint(1000, 10000),
                    'daily_icu_occupancy': np.random.randint(100, 1000)
                })
        
        hospital_df = pd.DataFrame(hospital)
        hospital_path = "data/raw/hospital.csv"
        hospital_df.to_csv(hospital_path, index=False)
        data_sets['hospital'] = hospital_path
        
        # 4. Testing
        testing = []
        for country in countries:
            for date in dates:
                testing.append({
                    'country': country,
                    'date': date.strftime('%Y-%m-%d'),
                    'new_tests': np.random.randint(50000, 200000),
                    'total_tests': np.random.randint(1000000, 10000000)
                })
        
        testing_df = pd.DataFrame(testing)
        testing_path = "data/raw/testing.csv"
        testing_df.to_csv(testing_path, index=False)
        data_sets['testing'] = testing_path
        
        return data_sets
    
    def validate_ml_data_availability(self) -> Dict:
        """Vérifie la disponibilité des données pour ML"""
        import os
        
        required_files = [
            "data/raw/cases_deaths.csv",
            "data/raw/vaccinations_global.csv",
            "data/raw/hospital.csv",
            "data/raw/testing.csv"
        ]
        
        status = {}
        for file_path in required_files:
            file_name = os.path.basename(file_path)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                status[file_name] = {
                    "exists": True,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "countries": df['country'].nunique() if 'country' in df.columns else 0
                }
            else:
                status[file_name] = {"exists": False}
        
        all_exist = all(file_info.get("exists", False) for file_info in status.values())
        
        return {
            "ready_for_training": all_exist,
            "files_status": status,
            "missing_files": [name for name, info in status.items() if not info.get("exists", False)]
        }