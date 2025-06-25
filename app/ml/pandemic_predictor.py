from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pandas as pd
import numpy as np
import joblib
from app.database.mongoClient import get_db

class PandemicPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.metrics = {}
        
    def prepare_data(self):
        """Prépare les données depuis MongoDB"""
        db = get_db()
        data = list(db.covid_data_oms.find().limit(50000))  # Limite pour performance
        df = pd.DataFrame(data)
        
        # Nettoyage
        df['date_reported'] = pd.to_datetime(df['date_reported'])
        df['new_cases'] = pd.to_numeric(df['new_cases'], errors='coerce').fillna(0)
        df['new_deaths'] = pd.to_numeric(df['new_deaths'], errors='coerce').fillna(0)
        
        # Features engineering
        df = df.sort_values(['country', 'date_reported'])
        df['cases_7day_avg'] = df.groupby('country')['new_cases'].rolling(7).mean().reset_index(0, drop=True)
        df['cases_lag1'] = df.groupby('country')['new_cases'].shift(1)
        df['cases_lag7'] = df.groupby('country')['new_cases'].shift(7)
        df['day_of_year'] = df['date_reported'].dt.dayofyear
        
        # Filtres
        df = df.dropna()
        df = df[df['new_cases'] >= 0]
        
        return df
    
    def train(self):
        """Entraîne le modèle Random Forest"""
        df = self.prepare_data()
        
        # Features et target
        features = ['cases_7day_avg', 'cases_lag1', 'cases_lag7', 'day_of_year']
        X = df[features].fillna(0)
        y = df['new_cases']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entraînement
        self.model.fit(X_train, y_train)
        
        # Prédictions et métriques
        y_pred = self.model.predict(X_test)
        
        self.metrics = {
            'r2_score': r2_score(y_test, y_pred),
            'mse': mean_squared_error(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'data_points': len(df),
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
        self.is_trained = True
        
        # Sauvegarde
        joblib.dump(self.model, '/api/pandemic_model.pkl')
        
        return self.metrics
    
    def predict(self, features):
        """Fait une prédiction"""
        if not self.is_trained:
            self.load_model()
        return self.model.predict([features])
    
    def load_model(self):
        """Charge le modèle sauvegardé"""
        try:
            self.model = joblib.load('/api/pandemic_model.pkl')
            self.is_trained = True
        except FileNotFoundError:
            raise ValueError("Modèle non trouvé. Entraînez d'abord avec train()")
    
    def get_feature_importance(self):
        """Retourne l'importance des features"""
        if not self.is_trained:
            raise ValueError("Modèle non entraîné")
        
        features = ['cases_7day_avg', 'cases_lag1', 'cases_lag7', 'day_of_year']
        importance = dict(zip(features, self.model.feature_importances_))
        return sorted(importance.items(), key=lambda x: x[1], reverse=True)