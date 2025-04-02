import base64
import io
from typing import List

import matplotlib.pyplot as plt
import networkx as nx

from ..models.component_health import ComponentHealthStatus, HealthCheckComponent


class SystemVisualizer:
    @staticmethod
    def create_graph_image(components: List[HealthCheckComponent]) -> str:
        """
        Create a visualization of the system graph and return it as a base64 encoded string.
        """
        G = nx.DiGraph()

        # Add nodes with their health status
        for component in components:
            color = (
                "green"
                if component.health_status == ComponentHealthStatus.HEALTHY
                else "red"
                if component.health_status == ComponentHealthStatus.UNHEALTHY
                else "gray"
            )
            G.add_node(component.id, name=component.name, color=color)

        # Add edges based on dependencies
        for component in components:
            for dep in component.dependencies:
                G.add_edge(component.id, dep)

        # Create the plot
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)

        # Draw nodes
        nx.draw_networkx_nodes(
            G,
            pos,
            node_color=[G.nodes[node]["color"] for node in G.nodes()],
            node_size=2000,
        )

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True)

        # Add labels
        labels = {node: G.nodes[node]["name"] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=10)

        plt.title("System Health Status Graph")
        plt.axis("off")

        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close()

        return base64.b64encode(buf.getvalue()).decode("utf-8")
