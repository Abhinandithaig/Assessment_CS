from src.system_health_checker.models.component_health import (
    ComponentHealthGraph,
    ComponentHealthStatus,
    HealthCheckComponent,
)


class TestHealthCheckComponent:
    def test_component_creation(self):
        # Arrange
        component_data = {
            "id": "test",
            "name": "Test Component",
            "dependencies": ["dep1"],
        }

        # Act
        component = HealthCheckComponent(**component_data)

        # Assert
        assert component.id == "test"
        assert component.name == "Test Component"
        assert component.dependencies == ["dep1"]
        assert component.health_status == ComponentHealthStatus.UNKNOWN
        assert component.last_checked is None


class TestComponentHealthGraph:
    def test_validate_valid_dag(self, simple_dag_components):
        # Arrange
        graph_data = {"components": simple_dag_components, "version": "1.0"}

        # Act
        graph = ComponentHealthGraph(**graph_data)
        is_valid = graph.validate_dag()

        # Assert
        assert is_valid is True

    def test_validate_cyclic_dag(self):
        # Arrange
        cyclic_components = [
            HealthCheckComponent(id="a", name="A", dependencies=["b"]),
            HealthCheckComponent(id="b", name="B", dependencies=["a"]),
        ]
        graph_data = {"components": cyclic_components, "version": "1.0"}

        # Act
        graph = ComponentHealthGraph(**graph_data)
        is_valid = graph.validate_dag()

        # Assert
        assert is_valid is False
