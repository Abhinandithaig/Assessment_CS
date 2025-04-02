import matplotlib # type: ignore
import pytest

matplotlib.use("Agg")  # Set non-interactive backend before importing pyplot

from src.system_health_checker.models.component_health import HealthCheckComponent


@pytest.fixture
def simple_dag_components():
    """Fixture providing a simple DAG with three components"""
    return [
        HealthCheckComponent(id="root", name="Root Service", dependencies=[]),
        HealthCheckComponent(id="middle", name="Middle Service", dependencies=["root"]),
        HealthCheckComponent(id="leaf", name="Leaf Service", dependencies=["middle"]),
    ]


@pytest.fixture
def complex_dag_components():
    """Fixture providing a complex DAG with parallel paths"""
    return [
        HealthCheckComponent(id="database", name="Database Service", dependencies=[]),
        HealthCheckComponent(
            id="cache", name="Cache Service", dependencies=["database"]
        ),
        HealthCheckComponent(id="auth", name="Auth Service", dependencies=["database"]),
        HealthCheckComponent(
            id="api", name="API Gateway", dependencies=["cache", "auth"]
        ),
    ]
