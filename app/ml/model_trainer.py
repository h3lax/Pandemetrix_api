import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import json
import os
from datetime import datetime
from typing import Dict, Tuple

class ModelTrainer:
    """Entraîneur de modèles ML pour Pandemetrix"""
    
    def __init__(self):
        self.data_path = "app/data/raw"
        self.model_path = "models/covid_polynomial_model.pkl"
        self.metadata_path = "models/model_metadata.json"
        
        # Créer les dossiers nécessaires
        os.makedirs("app/models", exist_ok=True)
        os.makedirs("app/data/processed", exist_ok=True)
    
    def load_and_merge_data(self) -> pd.DataFrame:
        """Charge et fusionne les données sources"""
        print("Chargement des données...")
        
        # Charger les fichiers
        df_cases = pd.read_csv(f"{self.data_path}/cases_deaths.csv")
        df_vaccines = pd.read_csv(f"{self.data_path}/vaccinations_global.csv")
        df_hospital = pd.read_csv(f"{self.data_path}/hospital.csv")
        df_testing = pd.read_csv(f"{self.data_path}/testing.csv")
        
        # Fusion progressive
        df_merge = pd.merge(df_cases, df_vaccines, on=["country", "date"], how="inner")
        df_merge = pd.merge(df_merge, df_hospital, on=["country", "date"], how="inner")
        df_merge = pd.merge(df_merge, df_testing, on=["country", "date"], how="inner")
        
        print(f"Données fusionnées: {df_merge.shape[0]} lignes, {df_merge.shape[1]} colonnes")
        return df_merge
    
    def prepare_data(self, df_merge: pd.DataFrame) -> pd.DataFrame:
        """Prépare et encode les données"""
        print("Préparation des données...")
        
        # Features requises
        required_features = ["date", "new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        target = "new_deaths"
        
        # Vérifier colonnes
        missing = [f for f in required_features + [target] if f not in df_merge.columns]
        if missing:
            raise ValueError(f"Colonnes manquantes: {missing}")
        
        # Sélectionner colonnes
        keep_cols = required_features + [target, "country"]
        data_filtered = df_merge[keep_cols].copy()
        
        # One-hot encoding des pays
        data_encoded = pd.get_dummies(data_filtered, columns=["country"], prefix="country1")
        
        # Nettoyage
        data_encoded.dropna(inplace=True)
        
        print(f"Données encodées: {data_encoded.shape[0]} lignes, {data_encoded.shape[1]} colonnes")
        return data_encoded
    
    def prepare_features(self, data_encoded: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, list]:
        """Prépare les features pour l'entraînement"""
        print("Préparation des features...")
        
        # Variable cible
        y = data_encoded["new_deaths"]
        
        # Conversion date
        data_encoded["date"] = pd.to_datetime(data_encoded["date"])
        data_encoded["date"] = data_encoded["date"].astype('int64') // 10**9
        
        # Features
        base_features = ["date", "new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        country_features = [col for col in data_encoded.columns if col.startswith("country1_")]
        all_features = base_features + country_features
        
        X = data_encoded[all_features]
        
        # Nettoyage final
        if X.isnull().any().any():
            mask = X.isnull().any(axis=1)
            X = X[~mask]
            y = y[~mask]
        
        print(f"Features finales: {X.shape[0]} lignes × {X.shape[1]} colonnes")
        return X, y, all_features
    
    def train_models(self, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                    y_train: pd.Series, y_test: pd.Series) -> Dict:
        """Entraîne les modèles baseline et polynomial"""
        print("Entraînement des modèles...")
        
        # Baseline
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        linear_model = LinearRegression()
        linear_model.fit(X_train_scaled, y_train)
        y_pred_baseline = linear_model.predict(X_test_scaled)
        
        baseline_r2 = r2_score(y_test, y_pred_baseline)
        baseline_mae = mean_absolute_error(y_test, y_pred_baseline)
        
        # Modèle polynomial avec GridSearch
        polynomial_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('poly', PolynomialFeatures()),
            ('ridge', Ridge())
        ])
        
        param_grid = {
            'poly__degree': [1, 2],
            'poly__interaction_only': [False, True],
            'ridge__alpha': [1.0, 10.0, 100.0, 1000.0]
        }
        
        grid_search = GridSearchCV(
            polynomial_pipeline, param_grid, cv=5, scoring='r2', n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        
        best_model = grid_search.best_estimator_
        y_pred_poly = best_model.predict(X_test)
        
        poly_r2 = r2_score(y_test, y_pred_poly)
        poly_mae = mean_absolute_error(y_test, y_pred_poly)
        
        print(f"Baseline - R²: {baseline_r2:.4f}, MAE: {baseline_mae:.4f}")
        print(f"Polynomial - R²: {poly_r2:.4f}, MAE: {poly_mae:.4f}")
        
        return {
            "baseline": {"model": linear_model, "scaler": scaler, "r2": baseline_r2, "mae": baseline_mae},
            "polynomial": {"model": best_model, "r2": poly_r2, "mae": poly_mae, 
                          "cv_score": grid_search.best_score_, "best_params": grid_search.best_params_}
        }
    
    def save_model_and_metadata(self, poly_model, features: list, baseline_results: Dict, 
                               poly_results: Dict, countries_list: list) -> None:
        """Sauvegarde le modèle et métadonnées"""
        print("Sauvegarde du modèle...")
        
        # Sauvegarder le modèle
        joblib.dump(poly_model, self.model_path)
        
        # Métadonnées
        base_features = ["date", "new_cases", "people_vaccinated", "new_tests", "daily_occupancy_hosp"]
        
        metadata = {
            "model_info": {
                "name": "COVID-19 Deaths Prediction Model",
                "type": "polynomial_regression_with_ridge",
                "version": "1.0",
                "training_date": datetime.now().isoformat(),
                "features_count": len(features),
                "countries_count": len(countries_list)
            },
            "features": {
                "all_features": features,
                "base_features": base_features,
                "country_features": countries_list
            },
            "hyperparameters": poly_results["best_params"],
            "performance": {
                "cross_validation_r2": poly_results["cv_score"],
                "test_r2": poly_results["r2"],
                "test_mae": poly_results["mae"],
                "baseline_r2": baseline_results["r2"],
                "baseline_mae": baseline_results["mae"],
                "improvement_r2_percent": ((poly_results["r2"] - baseline_results["r2"]) / baseline_results["r2"] * 100),
                "improvement_mae_percent": ((baseline_results["mae"] - poly_results["mae"]) / baseline_results["mae"] * 100)
            },
            "countries_supported": countries_list
        }
        
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)
        
        print(f"Modèle sauvé: {self.model_path}")
        print(f"Métadonnées: {self.metadata_path}")
    
    def train_model(self) -> Dict:
        """Pipeline complet d'entraînement"""
        try:
            # 1. Charger et fusionner
            df_merge = self.load_and_merge_data()
            
            # 2. Préparer données
            data_encoded = self.prepare_data(df_merge)
            X, y, features = self.prepare_features(data_encoded)
            
            # 3. Extraire pays
            countries_list = [col.replace("country1_", "") for col in features if col.startswith("country1_")]
            
            # 4. Split train/test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
            
            # 5. Entraîner modèles
            results = self.train_models(X_train, X_test, y_train, y_test)
            
            # 6. Sauvegarder
            self.save_model_and_metadata(
                results["polynomial"]["model"], features, 
                results["baseline"], results["polynomial"], countries_list
            )
            
            return {
                "status": "success",
                "data_points": len(X),
                "countries": len(countries_list),
                "performance": {
                    "baseline_r2": results["baseline"]["r2"],
                    "polynomial_r2": results["polynomial"]["r2"],
                    "improvement": ((results["polynomial"]["r2"] - results["baseline"]["r2"]) / results["baseline"]["r2"] * 100)
                },
                "model_path": self.model_path,
                "metadata_path": self.metadata_path
            }
            
        except Exception as e:
            raise Exception(f"Erreur entraînement: {str(e)}")