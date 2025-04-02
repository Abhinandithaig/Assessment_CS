from enum import Enum
from typing import List, Optional

import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, Field


class ComponentHealthStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckComponent(BaseModel):
    id: str = Field(..., description="Unique identifier for the component")
    name: str = Field(..., description="Display name of the component")
    dependencies: List[str] = Field(
        default_factory=list,
        description="List of component IDs this component depends on",
    )
    health_status: Optional[ComponentHealthStatus] = Field(
        default=ComponentHealthStatus.UNKNOWN,
        description="Current health status of the component",
    )
    last_checked: Optional[str] = Field(
        default=None, description="Timestamp of last health check"
    )


class ComponentHealthGraph(BaseModel):
    components: List[HealthCheckComponent] = Field(
        ..., description="List of all system components"
    )
    version: str = Field(default="1.0", description="Version of the system graph")

    def validate_dag(self) -> bool:
        """Validate that the graph is a DAG (no cycles)"""
        G = DiGraph()
        for component in self.components:
            G.add_node(component.id)
            for dep in component.dependencies:
                G.add_edge(component.id, dep)

        try:
            nx.find_cycle(G)
            return False
        except nx.NetworkXNoCycle:
            return True
