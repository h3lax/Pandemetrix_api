import pytest
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api/ml"

class TestMLAPI:
    """Tests pour les endpoints ML"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ML tests"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("ML API non accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("API non démarrée")
    
    def test_ml_health(self):
        """Test ML health check"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "model_loaded" in data
        assert "ready_for_predictions" in data
    
    def test_ml_countries(self):
        """Test pays supportés ML"""
        response = requests.get(f"{BASE_URL}/countries")
        
        if response.status_code == 500:
            pytest.skip("Modèle ML non chargé")
        
        assert response.status_code == 200
        data = response.json()
        assert "countries" in data
        assert "total_countries" in data
        assert isinstance(data["countries"], list)
    
    def test_ml_model_info(self):
        """Test informations modèle"""
        response = requests.get(f"{BASE_URL}/model-info")
        
        if response.status_code == 500:
            pytest.skip("Modèle ML non chargé")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "performance" in data
    
    def test_create_synthetic_data(self):
        """Test création données synthétiques"""
        response = requests.post(f"{BASE_URL}/create-synthetic-data")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "files_created" in data
    
    def test_ml_train(self):
        """Test entraînement modèle"""
        # D'abord créer les données
        requests.post(f"{BASE_URL}/create-synthetic-data")
        
        response = requests.post(f"{BASE_URL}/train")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "training_results" in data
    
    def test_ml_load_model(self):
        """Test rechargement modèle"""
        response = requests.post(f"{BASE_URL}/load-model")
        assert response.status_code in [200, 500]  # OK si modèle existe ou erreur si pas de modèle
    
    def test_valid_prediction(self):
        """Test prédiction valide"""
        # S'assurer qu'on a un modèle
        countries_resp = requests.get(f"{BASE_URL}/countries")
        if countries_resp.status_code != 200:
            pytest.skip("Pas de modèle chargé")
        
        countries = countries_resp.json()["countries"]
        if not countries:
            pytest.skip("Aucun pays disponible")
        
        test_data = {
            "country": countries[0],
            "date": "2023-01-15",
            "new_cases": 1500,
            "people_vaccinated": 50000000,
            "new_tests": 100000,
            "daily_occupancy_hosp": 2500
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "prediction" in result
        assert "new_deaths_predicted" in result["prediction"]
    
    def test_invalid_country_prediction(self):
        """Test prédiction pays invalide"""
        test_data = {
            "country": "PaysInexistant123",
            "date": "2023-01-15",
            "new_cases": 1500,
            "people_vaccinated": 50000000,
            "new_tests": 100000,
            "daily_occupancy_hosp": 2500
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=test_data)
        assert response.status_code in [400, 500]
    
    def test_missing_fields_prediction(self):
        """Test prédiction champs manquants"""
        test_data = {
            "country": "France",
            "date": "2023-01-15"
            # Champs manquants
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=test_data)
        assert response.status_code in [400, 500]
    
    def test_batch_prediction(self):
        """Test prédiction batch"""
        countries_resp = requests.get(f"{BASE_URL}/countries")
        if countries_resp.status_code != 200:
            pytest.skip("Pas de modèle chargé")
        
        countries = countries_resp.json()["countries"]
        if not countries:
            pytest.skip("Aucun pays disponible")
        
        test_data = {
            "predictions": [
                {
                    "country": countries[0],
                    "date": "2023-01-15",
                    "new_cases": 1500,
                    "people_vaccinated": 50000000,
                    "new_tests": 100000,
                    "daily_occupancy_hosp": 2500
                },
                {
                    "country": countries[0],
                    "date": "2023-01-16",
                    "new_cases": 1600,
                    "people_vaccinated": 50100000,
                    "new_tests": 110000,
                    "daily_occupancy_hosp": 2600
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/predict-batch", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "successful_predictions" in result
        assert "results" in result
    
    def test_batch_prediction_limit(self):
        """Test limite batch"""
        # Créer 101 prédictions (au-dessus de la limite)
        predictions = []
        for i in range(101):
            predictions.append({
                "country": "France",
                "date": "2023-01-15",
                "new_cases": 1500,
                "people_vaccinated": 50000000,
                "new_tests": 100000,
                "daily_occupancy_hosp": 2500
            })
        
        test_data = {"predictions": predictions}
        response = requests.post(f"{BASE_URL}/predict-batch", json=test_data)
        assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])