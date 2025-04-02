import json
import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..core.health_checker import HealthChecker
from ..models.component_health import ComponentHealthGraph
from ..utils.visualizer import SystemVisualizer

logger = logging.getLogger(__name__)
router = APIRouter()

health_checker = HealthChecker()
visualizer = SystemVisualizer()


@router.post("/upload-system")
async def upload_system(file: UploadFile = File(...)):
    """
    Upload a JSON file containing system component definitions.
    """
    try:
        content = await file.read()
        system_data = json.loads(content)
        system_graph = ComponentHealthGraph(**system_data)

        if not system_graph.validate_dag():
            raise HTTPException(
                status_code=400, detail="Invalid system graph: Contains cycles"
            )

        return {"message": "System graph uploaded successfully"}
    except Exception as e:
        logger.error(f"Error uploading system: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-health")
async def check_health(file: UploadFile = File(...)):
    """
    Check health of all system components.
    """
    try:
        content = await file.read()
        system_data = json.loads(content)
        system_graph = ComponentHealthGraph(**system_data)

        if not system_graph.validate_dag():
            raise HTTPException(
                status_code=400, detail="Invalid system graph: Contains cycles"
            )

        # Check health of all components
        updated_components = await health_checker.check_system_health(
            system_graph.components
        )

        # Generate summary
        summary = health_checker.get_system_status_summary(updated_components)

        # Generate visualization
        graph_image = visualizer.create_graph_image(updated_components)

        return JSONResponse(
            {
                "components": [comp.dict() for comp in updated_components],
                "summary": summary,
                "graph_image": graph_image,
            }
        )
    except Exception as e:
        logger.error(f"Error checking health: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Simple health check endpoint for the API itself.
    """
    return {"status": "healthy"}
