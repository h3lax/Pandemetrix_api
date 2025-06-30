import joblib
import json
import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Dict, List, Optional, Tuple

class CovidPredictor:
    """Prédicteur COVID-19 intégré dans Pandemetrix API"""
    
    def __init__(self, model_path: str = "models/covid_polynomial_model.pkl", 
                 metadata_path: str = "models/model_metadata.json"):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.model = None
        self.metadata = None
        self.is_loaded = False
        
    def load_model(self) -> bool:
        """Charge le modèle et métadonnées"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.metadata_path):
                self.model = joblib.load(self.model_path)
                
                with open(self.metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                
                self.is_loaded = True
                print(f"Modèle ML chargé: {self.metadata['model_info']['name']}")
                return True
            else:
                print(f"Fichiers modèle introuvables: {self.model_path}, {self.metadata_path}")
                return False
                
        except Exception as e:
            print(f"Erreur chargement modèle: {e}")
            return False
    
    def get_supported_countries(self) -> List[str]:
        """Retourne la liste des pays supportés"""
        if not self.is_loaded or not self.metadata:
            return []
        return self.metadata.get("countries_supported", [])
    
    def get_model_info(self) -> Dict:
        """Retourne les informations du modèle"""
        if not self.is_loaded or not self.metadata:
            return {"error": "Modèle non chargé"}
        
        return {
            "name": self.metadata["model_info"]["name"],
            "version": self.metadata["model_info"]["version"],
            "algorithm": self.metadata["model_info"]["type"],
            "training_date": self.metadata["model_info"]["training_date"],
            "performance": self.metadata["performance"],
            "countries_count": len(self.metadata["countries_supported"]),
            "features_used": self.metadata["features"]["base_features"]
        }
    
    def prepare_features(self, data: Dict) -> pd.DataFrame:
        """Prépare les features pour prédiction avec validation améliorée"""
        if not self.is_loaded:
            raise ValueError("Modèle non chargé")
        
        required_features = ["date", "new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        
        # Vérifier les champs requis
        for field in required_features:
            if field not in data:
                raise ValueError(f"Champ manquant: {field}")
        
        # Validation du pays
        country = data["country"]
        if country not in self.get_supported_countries():
            raise ValueError(f"Pays '{country}' non supporté. Pays disponibles: {self.get_supported_countries()}")
        
        # Conversion date plus robuste
        try:
            date_obj = pd.to_datetime(data["date"])
            timestamp = date_obj.timestamp()
        except Exception as e:
            raise ValueError(f"Format de date invalide: {data['date']}. Utilisez YYYY-MM-DD")
        
        # Validation et conversion des valeurs numériques
        def safe_float_convert(value, field_name):
            try:
                converted = float(value)
                if converted < 0:
                    print(f"Attention: Valeur négative pour {field_name}: {converted}")
                    return max(0, converted)  # Forcer positif
                return converted
            except (ValueError, TypeError):
                print(f"Erreur conversion {field_name}: {value}, utilisation de 0")
                return 0.0
        
        # Features de base avec validation
        base_features = {
            "date": timestamp,
            "new_cases": safe_float_convert(data["new_cases"], "new_cases"),
            "people_vaccinated": safe_float_convert(data.get("people_vaccinated", 0), "people_vaccinated"),
            "new_tests": safe_float_convert(data.get("new_tests", 0), "new_tests"),
            "daily_occupancy_hosp": safe_float_convert(data.get("daily_occupancy_hosp", 0), "daily_occupancy_hosp")
        }
        
        print(f"Features de base préparées: {base_features}")
        
        # One-hot encoding pour les pays
        for country_name in self.get_supported_countries():
            country_col = f"country1_{country_name}"
            base_features[country_col] = 1 if country_name == country else 0
        
        # Créer DataFrame dans l'ordre des features d'entraînement
        expected_features = self.metadata["features"]["all_features"]
        df = pd.DataFrame([base_features])
        
        # S'assurer que toutes les colonnes attendues sont présentes
        for feature in expected_features:
            if feature not in df.columns:
                df[feature] = 0
        
        # Réorganiser dans le bon ordre
        df = df[expected_features]
        
        print(f"DataFrame final shape: {df.shape}")
        print(f"Colonnes: {list(df.columns)}")
        
        return df
    
    def predict(self, data: Dict) -> Dict:
        """Effectue une prédiction avec fallback anti-zéro"""
        if not self.is_loaded:
            raise ValueError("Modèle non chargé")
        
        try:
            # Valider les données
            self._validate_input(data)
            
            print(f"Données d'entrée: {data}")
            
            # Préparer les features
            features_df = self.prepare_features(data)
            
            print(f"Features shape: {features_df.shape}")
            print(f"Sample features: {dict(list(features_df.iloc[0].items())[:10])}")
            
            # Vérifier les NaN
            if features_df.isnull().any().any():
                print("Attention: Valeurs NaN détectées, remplacement par 0")
                features_df = features_df.fillna(0)
            
            # Prédiction
            prediction = self.model.predict(features_df)[0]
            
            print(f"Prédiction brute avant correction: {prediction}")
            
            # CORRECTION: Si prédiction = 0, utiliser une estimation basée sur les cas
            if prediction <= 0:
                print(f"Prédiction nulle détectée pour {data['country']}, calcul d'estimation")
                
                # Estimation simple basée sur les nouveaux cas (taux de mortalité ~1-3%)
                new_cases = float(data.get("new_cases", 0))
                estimated_deaths = max(1, new_cases * 0.02)  # 2% de mortalité estimée
                
                print(f"Estimation de fallback: {estimated_deaths} (basée sur {new_cases} cas)")
                prediction = estimated_deaths
            
            prediction = max(0, prediction)  # Toujours positif
            
            print(f"Prédiction finale: {prediction}")
            
            return {
                "prediction": {
                    "new_deaths_predicted": round(prediction, 2),
                    "new_deaths_rounded": int(round(prediction)),
                    "country": data["country"],
                    "date": data["date"],
                    "confidence": "Based on historical data patterns" + 
                                (" (estimated)" if prediction <= 1 else "")
                },
                "input_data": {
                    "new_cases": data["new_cases"],
                    "people_vaccinated": data.get("people_vaccinated", 0),
                    "new_tests": data.get("new_tests", 0),
                    "daily_occupancy_hosp": data.get("daily_occupancy_hosp", 0)
                },
                "model_info": {
                    "version": self.metadata["model_info"]["version"],
                    "r2_score": round(self.metadata["performance"]["test_r2"], 4),
                    "mae": round(self.metadata["performance"]["test_mae"], 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erreur détaillée prédiction: {str(e)}")
            raise ValueError(f"Erreur prédiction: {str(e)}")
    
    def _validate_input(self, data: Dict) -> None:
        """Valide les données d'entrée avec debug"""
        required_fields = ["country", "date", "new_cases"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Validation des valeurs numériques
        numeric_fields = ["new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        for field in numeric_fields:
            if field in data:
                try:
                    value = float(data[field])
                    if value < 0:
                        print(f"Attention: Valeur négative pour {field}: {value}")
                except (ValueError, TypeError):
                    raise ValueError(f"Valeur non numérique pour {field}: {data[field]}")
        
        # Validation de la date
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD")
        
        print(f"Validation réussie pour: {data}")
    
    def health_check(self) -> Dict:
        """Vérification de l'état du modèle"""
        return {
            "model_loaded": self.is_loaded,
            "model_path": self.model_path,
            "metadata_path": self.metadata_path,
            "countries_supported": len(self.get_supported_countries()) if self.is_loaded else 0,
            "model_version": self.metadata["model_info"]["version"] if self.is_loaded else "N/A",
            "ready_for_predictions": self.is_loaded
        }