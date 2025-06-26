from flask_restx import Namespace, Resource, fields
from flask import request
from app.ml.covid_predictor import CovidPredictor
from app.models.ml_swagger import create_ml_swagger_models
import os

ml_api = Namespace("ml", description="Machine Learning COVID-19 Predictions")

# Créer les modèles Swagger
swagger_models = create_ml_swagger_models(ml_api)

# Instance globale du prédicteur
predictor = CovidPredictor()

@ml_api.route("/health")
class MLHealth(Resource):
    """Vérification santé ML"""
    
    @ml_api.marshal_with(swagger_models['ml_health'])
    @ml_api.doc('ml_health_check', description='Vérification de l\'état du système ML')
    def get(self):
        """ML health check"""
        return predictor.health_check(), 200

@ml_api.route("/countries")
class MLCountries(Resource):
    def get(self):
        if not predictor.is_loaded:
            return {
                "countries": [],
                "total_countries": 0,
                "sample_countries": [],
                "note": "Model not loaded. Train the model first."
            }, 200  # 200 au lieu de 500
        
        countries = predictor.get_supported_countries()
        return {
            "countries": sorted(countries),
            "total_countries": len(countries),
            "sample_countries": countries[:5],
            "note": "Use exact country names for predictions"
        }, 200

@ml_api.route("/model-info")
class MLModelInfo(Resource):
    def get(self):
        if not predictor.is_loaded:
            return {
                "error": "Model not loaded",
                "message": "Train the model first using the button below"
            }, 200  # 200 au lieu de 500
        
        return predictor.get_model_info(), 200

@ml_api.route("/predict")
class MLPredict(Resource):
    """Prédiction unique"""
    
    @ml_api.expect(swagger_models['ml_prediction_input'])
    @ml_api.marshal_with(swagger_models['ml_prediction_output'])
    @ml_api.doc('ml_predict', description='Effectue une prédiction de mortalité COVID-19')
    @ml_api.response(200, 'Prédiction réussie')
    @ml_api.response(400, 'Données invalides')
    @ml_api.response(500, 'Erreur serveur')
    def post(self):
        """Make a single COVID-19 death prediction"""
        try:
            if not predictor.is_loaded:
                ml_api.abort(500, "Model not loaded")
            
            data = request.get_json()
            if not data:
                ml_api.abort(400, "JSON data required")
            
            result = predictor.predict(data)
            return result, 200
            
        except ValueError as e:
            ml_api.abort(400, str(e))
        except Exception as e:
            ml_api.abort(500, f"Prediction error: {str(e)}")

@ml_api.route("/predict-batch")
class MLPredictBatch(Resource):
    """Prédictions multiples"""
    
    @ml_api.expect(swagger_models['ml_batch_input'])
    @ml_api.marshal_with(swagger_models['ml_batch_output'])
    @ml_api.doc('ml_predict_batch', description='Effectue plusieurs prédictions COVID-19 en une fois')
    @ml_api.response(200, 'Prédictions réussies')
    @ml_api.response(400, 'Format de données invalide')
    @ml_api.response(500, 'Erreur serveur')
    def post(self):
        """Make multiple COVID-19 death predictions"""
        try:
            if not predictor.is_loaded:
                ml_api.abort(500, "Model not loaded")
            
            data = request.get_json()
            if not data or "predictions" not in data:
                ml_api.abort(400, "Format: {'predictions': [...]}")
            
            predictions_list = data["predictions"]
            if not isinstance(predictions_list, list):
                ml_api.abort(400, "predictions must be a list")
            
            if len(predictions_list) > 100:
                ml_api.abort(400, "Maximum 100 predictions per batch")
            
            result = predictor.predict_batch(predictions_list)
            return result, 200
            
        except Exception as e:
            ml_api.abort(500, f"Batch prediction error: {str(e)}")

@ml_api.route("/load-model")
class MLLoadModel(Resource):
    """Rechargement du modèle"""
    
    @ml_api.doc('ml_load_model', description='Recharge le modèle ML depuis le disque')
    @ml_api.response(200, 'Modèle rechargé avec succès')
    @ml_api.response(500, 'Échec du chargement')
    def post(self):
        """Reload ML model"""
        try:
            success = predictor.load_model()
            if success:
                return {"message": "Model loaded successfully", "model_info": predictor.get_model_info()}, 200
            else:
                ml_api.abort(500, "Failed to load model")
        except Exception as e:
            ml_api.abort(500, f"Load error: {str(e)}")

@ml_api.route("/train")
class MLTrain(Resource):
    def post(self):
        try:
            from app.ml.model_trainer import ModelTrainer
            trainer = ModelTrainer()
            
            # Corriger les chemins
            required_files = [
                "app/data/raw/cases_deaths.csv",
                "app/data/raw/vaccinations_global.csv", 
                "app/data/raw/hospital.csv",
                "app/data/raw/testing.csv"
            ]
            
            missing_files = [f for f in required_files if not os.path.exists(f)]
            if missing_files:
                return {
                    "error": "Missing data files for training",
                    "missing_files": missing_files,
                    "note": "Upload data files to train the model"
                }, 400
            
            result = trainer.train_model()
            predictor.load_model()
            
            return {
                "message": "Model trained successfully",
                "training_results": result,
                "model_reloaded": predictor.is_loaded
            }, 200
            
        except Exception as e:
            return {"error": f"Training error: {str(e)}"}, 500

@ml_api.route("/create-synthetic-data")
class MLCreateSyntheticData(Resource):
    """Création de données synthétiques pour tests"""
    
    @ml_api.doc('ml_create_synthetic_data', description='Génère des données synthétiques pour tests et développement')
    @ml_api.response(200, 'Données créées avec succès')
    @ml_api.response(500, 'Erreur de génération')
    def post(self):
        """Create synthetic data for testing"""
        try:
            from app.ml.data_processor import MLDataProcessor
            processor = MLDataProcessor()
            data_sets = processor.create_synthetic_ml_data()
            
            return {
                "message": "Synthetic data created successfully",
                "files_created": data_sets,
                "note": "You can now train the model with /api/ml/train"
            }, 200
            
        except Exception as e:
            ml_api.abort(500, f"Data generation error: {str(e)}")

# Initialiser le modèle au démarrage
def init_ml_predictor():
    """Initialise le prédicteur ML"""
    global predictor
    success = predictor.load_model()
    if success:
        print("✅ Modèle ML chargé avec succès")
    else:
        print("⚠️ Modèle ML non trouvé - utilisez /ml/train pour l'entraîner")
    return success

@ml_api.route("/load-csv-data")
class MLLoadCSVData(Resource):
    def post(self):
        try:
            from app.ml.data_processor import MLDataProcessor
            processor = MLDataProcessor()
            
            # Juste le chargement, pas la préparation
            results = processor.load_csv_to_mongodb()
            
            return {
                "message": "CSV loading attempted",
                "mongodb_results": results
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500