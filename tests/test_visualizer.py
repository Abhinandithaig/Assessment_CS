import base64

import matplotlib
import pytest

matplotlib.use("Agg")  # Force non-interactive backend

from system_health_checker.utils.visualizer import SystemVisualizer


class TestSystemVisualizer:
    def test_create_graph_image(self, simple_dag_components):
        """Test graph visualization generation"""
        visualizer = SystemVisualizer()

        try:
            # Generate graph image
            image_base64 = visualizer.create_graph_image(simple_dag_components)

            # Verify it's valid base64
            assert isinstance(image_base64, str)
            decoded = base64.b64decode(image_base64)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Failed to create graph image: {str(e)}")
        finally:
            # Clean up any open figures
            import matplotlib.pyplot as plt

            plt.close("all")
