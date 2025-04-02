import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, List

from ..models.component_health import ComponentHealthStatus, HealthCheckComponent

logger = logging.getLogger(__name__)


class HealthChecker:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def check_component_health(
        self, component: HealthCheckComponent
    ) -> HealthCheckComponent:
        """
        Simulate health check for a component with random status.
        In a real implementation, this would make actual API calls to check component health.
        """
        self.logger.info(f"Checking health for component: {component.id}")

        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Randomly determine health status
        is_healthy = random.random() > 0.3  # 70% chance of being healthy

        component.health_status = (
            ComponentHealthStatus.HEALTHY
            if is_healthy
            else ComponentHealthStatus.UNHEALTHY
        )
        component.last_checked = datetime.utcnow().isoformat()

        self.logger.info(
            f"Component {component.id} health status: {component.health_status}"
        )
        return component

    async def check_system_health(
        self, components: List[HealthCheckComponent]
    ) -> List[HealthCheckComponent]:
        """
        Check health of all components using BFS traversal.
        Components are checked in level order, with parallel health checks within each level.
        """
        # Create a mapping of component ID to component for easy lookup
        comp_map = {comp.id: comp for comp in components}

        # Validate all dependencies exist
        for comp in components:
            for dep_id in comp.dependencies:
                if dep_id not in comp_map:
                    raise ValueError(
                        f"Component {comp.id} has missing dependency: {dep_id}"
                    )

        # Start with nodes that have no dependencies (root nodes)
        queue = [comp for comp in components if not comp.dependencies]
        if not queue:
            raise ValueError("No root components found (cycle detected)")

        visited = set()
        results = []

        # Process components level by level (BFS)
        while queue:
            # Process all components at current level in parallel
            current_level = queue[:]
            queue = []

            # Check health of all components in current level
            level_tasks = []
            for comp in current_level:
                if comp.id not in visited:
                    level_tasks.append(self.check_component_health(comp))
                    visited.add(
                        comp.id
                    )  # Mark as visited before check to prevent duplicates

            checked_components = await asyncio.gather(*level_tasks)
            results.extend(checked_components)

            # Use comp_map to efficiently find dependents
            for checked_comp in checked_components:
                # Find components that depend on the checked component
                for comp_id, comp in comp_map.items():
                    if (
                        comp_id not in visited
                        and checked_comp.id in comp.dependencies
                        and all(dep in visited for dep in comp.dependencies)
                    ):
                        queue.append(comp)

        # Verify all components were checked
        if len(visited) != len(components):
            unchecked = set(comp_map.keys()) - visited
            raise ValueError(f"Some components were not checked: {unchecked}")

        return results

    def get_system_status_summary(self, components: List[HealthCheckComponent]) -> Dict:
        """
        Generate a summary of the system health status.
        """
        total = len(components)
        healthy = sum(
            1 for c in components if c.health_status == ComponentHealthStatus.HEALTHY
        )
        unhealthy = sum(
            1 for c in components if c.health_status == ComponentHealthStatus.UNHEALTHY
        )
        unknown = sum(
            1 for c in components if c.health_status == ComponentHealthStatus.UNKNOWN
        )

        return {
            "total_components": total,
            "healthy_components": healthy,
            "unhealthy_components": unhealthy,
            "unknown_components": unknown,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
        }
