import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from system_health_checker.api.main import app

client = TestClient(app)


class TestHealthCheckAPI:
    def test_health_endpoint(self):
        # Arrange
        expected_response = {"status": "healthy"}

        # Act
        response = client.get("/api/v1/health")

        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response

    @pytest.mark.asyncio
    async def test_check_health_endpoint(self, simple_dag_components):
        """Test health check endpoint with sample DAG"""
        dag_json = {
            "components": [comp.dict() for comp in simple_dag_components],
            "version": "1.0",
        }
        files = {"file": ("test.json", json.dumps(dag_json), "application/json")}

        # Mock the visualization to avoid matplotlib issues
        with patch(
            "system_health_checker.utils.visualizer.SystemVisualizer.create_graph_image"
        ) as mock_viz:
            mock_viz.return_value = "mock_base64_image"
            response = client.post("/api/v1/check-health", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "summary" in data
        assert data["graph_image"] == "mock_base64_image"

    def test_check_health_invalid_json(self):
        # Arrange
        files = {"file": ("test.json", "invalid json", "application/json")}

        # Act
        response = client.post("/api/v1/check-health", files=files)

        # Assert
        assert response.status_code == 500
