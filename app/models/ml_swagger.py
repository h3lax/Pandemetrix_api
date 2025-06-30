"""Modèles Swagger pour les endpoints ML"""
from flask_restx import fields

def create_ml_swagger_models(api):
    """Crée les modèles Swagger pour ML"""
    
    # Input models
    ml_prediction_input = api.model('MLPredictionInput', {
        'country': fields.String(
            required=True, 
            description='Nom du pays exact (voir /api/ml/countries)', 
            example='France'
        ),
        'date': fields.String(
            required=True, 
            description='Date format YYYY-MM-DD', 
            example='2023-01-15'
        ),
        'new_cases': fields.Float(
            required=True, 
            description='Nouveaux cas COVID-19', 
            example=1500.0,
            min=0
        ),
        'people_vaccinated': fields.Float(
            required=True, 
            description='Total personnes vaccinées (1+ dose)', 
            example=50000000,
            min=0
        ),
        'new_tests': fields.Float(
            required=True, 
            description='Nouveaux tests COVID-19', 
            example=100000,
            min=0
        ),
        'daily_occupancy_hosp': fields.Float(
            required=True, 
            description='Occupation hospitalière COVID', 
            example=2500,
            min=0
        )
    })
    
    ml_batch_input = api.model('MLBatchInput', {
        'predictions': fields.List(
            fields.Nested(ml_prediction_input), 
            required=True, 
            description='Liste des prédictions (max 100)',
            min_items=1,
            max_items=100
        )
    })
    
    # Output models
    ml_prediction_result = api.model('MLPredictionResult', {
        'new_deaths_predicted': fields.Float(description='Décès prédits', example=45.2),
        'new_deaths_rounded': fields.Integer(description='Décès prédits (entier)', example=45),
        'country': fields.String(description='Pays', example='France'),
        'date': fields.String(description='Date', example='2023-01-15'),
        'confidence': fields.String(description='Niveau de confiance')
    })
    
    ml_input_data = api.model('MLInputData', {
        'new_cases': fields.Float(example=1500),
        'people_vaccinated': fields.Float(example=50000000),
        'new_tests': fields.Float(example=100000),
        'daily_occupancy_hosp': fields.Float(example=2500)
    })
    
    ml_model_info = api.model('MLModelInfo', {
        'version': fields.String(example='1.0'),
        'r2_score': fields.Float(example=0.876),
        'mae': fields.Float(example=31.02)
    })
    
    ml_prediction_output = api.model('MLPredictionOutput', {
        'prediction': fields.Nested(ml_prediction_result),
        'input_data': fields.Nested(ml_input_data),
        'model_info': fields.Nested(ml_model_info),
        'timestamp': fields.String(description='Horodatage ISO')
    })
    
    ml_batch_result = api.model('MLBatchResult', {
        'index': fields.Integer(description='Index dans le batch'),
        'country': fields.String(description='Pays'),
        'date': fields.String(description='Date'),
        'new_deaths_predicted': fields.Float(description='Prédiction')
    })
    
    ml_batch_error = api.model('MLBatchError', {
        'index': fields.Integer(description='Index de l\'erreur'),
        'error': fields.String(description='Message d\'erreur')
    })
    
    ml_batch_output = api.model('MLBatchOutput', {
        'successful_predictions': fields.Integer(description='Prédictions réussies'),
        'failed_predictions': fields.Integer(description='Prédictions échouées'),
        'results': fields.List(fields.Nested(ml_batch_result)),
        'errors': fields.List(fields.Nested(ml_batch_error)),
        'model_version': fields.String(description='Version du modèle'),
        'timestamp': fields.String(description='Horodatage')
    })
    
    # Status models
    ml_health = api.model('MLHealth', {
        'model_loaded': fields.Boolean(description='Modèle chargé'),
        'model_path': fields.String(description='Chemin du modèle'),
        'countries_supported': fields.Integer(description='Nombre de pays'),
        'model_version': fields.String(description='Version'),
        'ready_for_predictions': fields.Boolean(description='Prêt pour prédictions')
    })
    
    ml_countries = api.model('MLCountries', {
        'countries': fields.List(fields.String, description='Liste des pays'),
        'total_countries': fields.Integer(description='Nombre total'),
        'sample_countries': fields.List(fields.String, description='Échantillon'),
        'note': fields.String(description='Note d\'utilisation')
    })
    
    ml_model_details = api.model('MLModelDetails', {
        'name': fields.String(description='Nom du modèle'),
        'version': fields.String(description='Version'),
        'algorithm': fields.String(description='Algorithme'),
        'training_date': fields.String(description='Date d\'entraînement'),
        'performance': fields.Raw(description='Métriques de performance'),
        'countries_count': fields.Integer(description='Nombre de pays'),
        'features_used': fields.List(fields.String, description='Features utilisées')
    })
    
    # Training models
    ml_training_result = api.model('MLTrainingResult', {
        'status': fields.String(description='Statut', example='success'),
        'data_points': fields.Integer(description='Points de données'),
        'countries': fields.Integer(description='Nombre de pays'),
        'performance': fields.Raw(description='Performance du modèle'),
        'model_path': fields.String(description='Chemin du modèle'),
        'metadata_path': fields.String(description='Chemin métadonnées')
    })
    
    # Error model
    ml_error = api.model('MLError', {
        'error': fields.String(description='Message d\'erreur'),
        'details': fields.Raw(description='Détails de l\'erreur')
    })
    
    return {
        'ml_prediction_input': ml_prediction_input,
        'ml_batch_input': ml_batch_input,
        'ml_prediction_output': ml_prediction_output,
        'ml_batch_output': ml_batch_output,
        'ml_health': ml_health,
        'ml_countries': ml_countries,
        'ml_model_details': ml_model_details,
        'ml_training_result': ml_training_result,
        'ml_error': ml_error
    }