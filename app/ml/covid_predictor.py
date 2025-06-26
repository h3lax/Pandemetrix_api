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
        """Prépare les features pour prédiction"""
        if not self.is_loaded:
            raise ValueError("Modèle non chargé")
        
        required_features = ["date", "new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        
        # Vérifier les champs requis
        for field in required_features:
            if field not in data:
                raise ValueError(f"Champ manquant: {field}")
        
        # Features de base
        base_features = {
            "date": pd.Timestamp(data["date"]).timestamp(),
            "new_cases": float(data["new_cases"]),
            "people_vaccinated": float(data.get("people_vaccinated", 0)),
            "new_tests": float(data.get("new_tests", 0)),
            "daily_occupancy_hosp": float(data.get("daily_occupancy_hosp", 0))
        }
        
        # Validation du pays
        country = data["country"]
        if country not in self.get_supported_countries():
            raise ValueError(f"Pays '{country}' non supporté. Pays disponibles: {self.get_supported_countries()}")
        
        # One-hot encoding pour les pays
        for country_name in self.get_supported_countries():
            country_col = f"country1_{country_name}"
            base_features[country_col] = 1 if country_name == country else 0
        
        # Créer DataFrame dans l'ordre des features d'entraînement
        expected_features = self.metadata["features"]["all_features"]
        df = pd.DataFrame([base_features])
        df = df[expected_features]
        
        return df
    
    def predict(self, data: Dict) -> Dict:
        """Effectue une prédiction"""
        if not self.is_loaded:
            raise ValueError("Modèle non chargé")
        
        try:
            # Valider les données
            self._validate_input(data)
            
            # Préparer les features
            features_df = self.prepare_features(data)
            
            # Prédiction
            prediction = self.model.predict(features_df)[0]
            prediction = max(0, prediction)  # Pas de valeurs négatives
            
            return {
                "prediction": {
                    "new_deaths_predicted": round(prediction, 2),
                    "new_deaths_rounded": int(round(prediction)),
                    "country": data["country"],
                    "date": data["date"],
                    "confidence": "Based on historical data patterns"
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
            raise ValueError(f"Erreur prédiction: {str(e)}")
    
    def predict_batch(self, predictions_list: List[Dict]) -> Dict:
        """Effectue des prédictions multiples"""
        if not self.is_loaded:
            raise ValueError("Modèle non chargé")
        
        results = []
        errors = []
        
        for i, pred_data in enumerate(predictions_list):
            try:
                result = self.predict(pred_data)
                results.append({
                    "index": i,
                    "country": pred_data["country"],
                    "date": pred_data["date"],
                    "new_deaths_predicted": result["prediction"]["new_deaths_predicted"]
                })
            except Exception as e:
                errors.append({"index": i, "error": str(e)})
        
        return {
            "successful_predictions": len(results),
            "failed_predictions": len(errors),
            "results": results,
            "errors": errors if errors else None,
            "model_version": self.metadata["model_info"]["version"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_input(self, data: Dict) -> None:
        """Valide les données d'entrée"""
        required_fields = ["country", "date", "new_cases"]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Validation des valeurs numériques
        if data.get("new_cases", 0) < 0:
            raise ValueError("new_cases doit être positif")
        
        # Validation de la date
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD")
    
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