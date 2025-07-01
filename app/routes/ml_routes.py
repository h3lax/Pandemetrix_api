# app/routes/ml_routes.py - Modifié pour proxifier vers Pandemetrix_ML
from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
import requests
import json
import os
from datetime import datetime

ml_api = Namespace("ml", description="Machine Learning COVID-19 Predictions (Proxy vers Pandemetrix_ML)")

# Configuration de l'API Pandemetrix_ML
PANDEMETRIX_ML_BASE_URL = os.getenv('PANDEMETRIX_ML_URL', 'http://localhost:5001/api/v1/covid')

# Modèles Swagger simplifiés pour compatibilité
ml_health = ml_api.model('MLHealth', {
    'model_loaded': fields.Boolean(description='Modèle chargé'),
    'ready_for_predictions': fields.Boolean(description='Prêt pour prédictions'),
    'model_version': fields.String(description='Version du modèle'),
    'status': fields.String(description='Statut général')
})

ml_prediction_input = ml_api.model('MLPredictionInput', {
    'country': fields.String(required=True, description='Pays', example='France'),
    'date': fields.String(required=True, description='Date YYYY-MM-DD', example='2023-01-15'),
    'new_cases': fields.Float(required=True, description='Nouveaux cas', example=1500.0),
    'people_vaccinated': fields.Float(required=True, description='Personnes vaccinées', example=50000000.0),
    'new_tests': fields.Float(required=True, description='Nouveaux tests', example=100000.0),
    'daily_occupancy_hosp': fields.Float(required=True, description='Occupation hospitalière', example=2500.0)
})

ml_batch_input = ml_api.model('MLBatchInput', {
    'predictions': fields.List(fields.Nested(ml_prediction_input), required=True, description='Liste des prédictions')
})

def make_pandemetrix_request(endpoint, method='GET', data=None):
    """Fonction utilitaire pour faire des requêtes vers Pandemetrix_ML"""
    url = f"{PANDEMETRIX_ML_BASE_URL}/{endpoint.lstrip('/')}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=30)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=30)
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")
        
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Pandemetrix_ML API non accessible", "url": url}, 503
    except requests.exceptions.Timeout:
        return {"error": "Timeout vers Pandemetrix_ML API"}, 504
    except Exception as e:
        return {"error": f"Erreur connexion Pandemetrix_ML: {str(e)}"}, 500

@ml_api.route("/health")
class MLHealth(Resource):
    """Vérification santé ML (proxy)"""
    
    @ml_api.marshal_with(ml_health)
    @ml_api.doc('ml_health_check', description='Vérification de l\'état du système ML')
    def get(self):
        """ML health check via Pandemetrix_ML"""
        data, status_code = make_pandemetrix_request('health')
        
        if status_code != 200:
            return data, status_code
        
        # Adapter la réponse au format attendu
        adapted_response = {
            'model_loaded': data.get('model_loaded', False),
            'ready_for_predictions': data.get('ready_for_predictions', False),
            'model_version': data.get('model_version', 'unknown'),
            'status': data.get('status', 'unknown')
        }
        
        return adapted_response, 200

@ml_api.route("/countries")
class MLCountries(Resource):
    @ml_api.doc('ml_countries', description='Pays supportés par le modèle ML')
    def get(self):
        """Récupère les pays supportés via Pandemetrix_ML"""
        data, status_code = make_pandemetrix_request('countries')
        return data, status_code

@ml_api.route("/model-info")
class MLModelInfo(Resource):
    @ml_api.doc('ml_model_info', description='Informations sur le modèle ML')
    def get(self):
        """Informations du modèle via Pandemetrix_ML"""
        data, status_code = make_pandemetrix_request('model-info')
        
        if status_code != 200:
            return data, status_code
        
        # Adapter la structure pour compatibilité avec l'ancien format
        try:
            adapted_response = {
                "name": data.get("model_info", {}).get("name", "COVID-19 Deaths Prediction Model"),
                "version": data.get("model_info", {}).get("version", "1.0"),
                "algorithm": data.get("model_info", {}).get("type", "polynomial_regression_with_ridge"),
                "training_date": data.get("model_info", {}).get("training_date", datetime.now().isoformat()),
                "countries_count": data.get("model_info", {}).get("countries_count", 0),
                "features_used": data.get("data_info", {}).get("features_used", []),
                "performance": data.get("performance", {})
            }
            return adapted_response, 200
        except Exception as e:
            return {"error": f"Erreur adaptation réponse: {str(e)}", "raw_data": data}, 500

@ml_api.route("/predict")
class MLPredict(Resource):
    """Prédiction unique (utilise predict-batch de Pandemetrix_ML avec 1 élément)"""
    
    @ml_api.expect(ml_prediction_input)
    @ml_api.doc('ml_predict', description='Effectue une prédiction de mortalité COVID-19')
    def post(self):
        """Make a single COVID-19 death prediction via Pandemetrix_ML"""
        try:
            data = request.get_json()
            if not data:
                return {"error": "JSON data required"}, 400
            
            # Encapsuler dans un format batch avec un seul élément
            batch_data = {"predictions": [data]}
            
            result, status_code = make_pandemetrix_request('predict-batch', 'POST', batch_data)
            
            if status_code != 200:
                return result, status_code
            
            # Adapter la réponse pour correspondre au format de prédiction simple
            if result.get("results") and len(result["results"]) > 0:
                first_result = result["results"][0]
                adapted_response = {
                    "prediction": {
                        "new_deaths_predicted": first_result.get("new_deaths_predicted", 0),
                        "new_deaths_rounded": round(first_result.get("new_deaths_predicted", 0)),
                        "country": data.get("country"),
                        "date": data.get("date"),
                        "confidence": "Based on historical data patterns"
                    },
                    "input_data": data,
                    "model_info": {
                        "version": result.get("model_version", "1.0"),
                        "r2_score": 0.82,  # Valeur par défaut
                        "mae": 45.4
                    },
                    "timestamp": result.get("timestamp", datetime.now().isoformat())
                }
                return adapted_response, 200
            else:
                return {"error": "Aucun résultat de prédiction"}, 500
                
        except Exception as e:
            return {"error": f"Erreur prédiction: {str(e)}"}, 500

@ml_api.route("/predict-batch")
class MLPredictBatch(Resource):
    """Prédictions multiples (proxy direct vers Pandemetrix_ML)"""
    
    @ml_api.expect(ml_batch_input)
    @ml_api.doc('ml_predict_batch', description='Effectue plusieurs prédictions COVID-19')
    def post(self):
        """Make multiple COVID-19 death predictions via Pandemetrix_ML"""
        try:
            data = request.get_json()
            if not data or "predictions" not in data:
                return {"error": "Format: {'predictions': [...]}"}, 400
            
            result, status_code = make_pandemetrix_request('predict-batch', 'POST', data)
            return result, status_code
            
        except Exception as e:
            return {"error": f"Erreur prédiction batch: {str(e)}"}, 500