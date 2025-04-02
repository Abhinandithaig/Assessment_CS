import pytest

from system_health_checker.core.health_checker import HealthChecker
from system_health_checker.models.component_health import (
    ComponentHealthStatus,
    HealthCheckComponent,
)


class TestHealthChecker:
    @pytest.mark.asyncio
    async def test_check_component_health(self):
        # Arrange
        checker = HealthChecker()
        component = HealthCheckComponent(
            id="test", name="Test Component", dependencies=[]
        )

        # Act
        result = await checker.check_component_health(component)

        # Assert
        assert result.id == "test"
        assert result.health_status in [
            ComponentHealthStatus.HEALTHY,
            ComponentHealthStatus.UNHEALTHY,
        ]
        assert result.last_checked is not None

    @pytest.mark.asyncio
    async def test_check_system_health_bfs_order(self, complex_dag_components):
        # Arrange
        checker = HealthChecker()

        # Act
        results = await checker.check_system_health(complex_dag_components)

        # Assert
        result_order = [comp.id for comp in results]
        database_idx = result_order.index("database")
        cache_idx = result_order.index("cache")
        auth_idx = result_order.index("auth")
        api_idx = result_order.index("api")

        # Verify BFS order
        assert database_idx == 0  # Root should be first
        assert cache_idx < api_idx  # Dependencies before dependents
        assert auth_idx < api_idx

    def test_get_system_status_summary(self, simple_dag_components):
        # Arrange
        checker = HealthChecker()
        simple_dag_components[0].health_status = ComponentHealthStatus.HEALTHY
        simple_dag_components[1].health_status = ComponentHealthStatus.UNHEALTHY
        simple_dag_components[2].health_status = ComponentHealthStatus.HEALTHY

        # Act
        summary = checker.get_system_status_summary(simple_dag_components)

        # Assert
        assert summary["total_components"] == 3
        assert summary["healthy_components"] == 2
        assert summary["unhealthy_components"] == 1
        assert summary["health_percentage"] == pytest.approx(66.67, rel=0.01)
