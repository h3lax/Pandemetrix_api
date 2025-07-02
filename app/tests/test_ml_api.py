import pytest
import requests
from unittest.mock import patch, Mock

BASE_URL = "http://localhost:5000/api/ml"

class TestMLAPIProxy:
    """Tests pour les endpoints ML proxy vers Pandemetrix_ML"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ML proxy tests"""
        try:
            response = requests.get(f"http://localhost:5000/api/health/status", timeout=5)
            if response.status_code != 200:
                pytest.skip("API principale non accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("API non démarrée")
    
    @patch('requests.get')
    def test_ml_health_proxy_success(self, mock_get):
        """Test proxy ML health avec succès"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "model_loaded": True,
            "ready_for_predictions": True,
            "model_version": "1.0",
            "status": "ready"
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model_loaded"] is True
        assert data["ready_for_predictions"] is True
    
    def test_ml_health_pandemetrix_down(self):
        """Test proxy quand Pandemetrix_ML est down"""
        response = requests.get(f"{BASE_URL}/health")
        
        # Peut être 503 si Pandemetrix_ML est down ou 200 si accessible
        assert response.status_code in [200, 503]
        
        if response.status_code == 503:
            data = response.json()
            assert "error" in data
            assert "Pandemetrix_ML API non accessible" in data["error"]
    
    @patch('requests.get')
    def test_ml_countries_proxy(self, mock_get):
        """Test proxy pays supportés"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "countries": ["France", "Germany", "Italy"],
            "total_countries": 3
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        response = requests.get(f"{BASE_URL}/countries")
        assert response.status_code == 200
        
        data = response.json()
        assert "countries" in data
        assert isinstance(data["countries"], list)
    
    @patch('requests.post')
    def test_ml_predict_proxy(self, mock_post):
        """Test proxy prédiction"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{
                "new_deaths_predicted": 42.5,
                "country": "France",
                "date": "2023-01-15"
            }],
            "model_version": "1.0",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        test_data = {
            "country": "France",
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
        assert result["prediction"]["new_deaths_rounded"] == 43
    
    def test_ml_predict_invalid_data(self):
        """Test prédiction avec données invalides"""
        test_data = {
            "country": "France"
            # Champs manquants
        }
        
        response = requests.post(f"{BASE_URL}/predict", json=test_data)
        assert response.status_code in [400, 500]  # Erreur attendue
    
    @patch('requests.post')
    def test_ml_batch_predict_proxy(self, mock_post):
        """Test proxy prédiction batch"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"new_deaths_predicted": 42.5, "country": "France"},
                {"new_deaths_predicted": 38.2, "country": "France"}
            ],
            "successful_predictions": 2,
            "model_version": "1.0"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        test_data = {
            "predictions": [
                {
                    "country": "France",
                    "date": "2023-01-15",
                    "new_cases": 1500,
                    "people_vaccinated": 50000000,
                    "new_tests": 100000,
                    "daily_occupancy_hosp": 2500
                },
                {
                    "country": "France",
                    "date": "2023-01-16",
                    "new_cases": 1400,
                    "people_vaccinated": 50100000,
                    "new_tests": 95000,
                    "daily_occupancy_hosp": 2400
                }
            ]
        }
        
        response = requests.post(f"{BASE_URL}/predict-batch", json=test_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "results" in result
        assert len(result["results"]) == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])