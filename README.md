# System Health Checker

A Python web API that checks the health of system components organized in a Directed Acyclic Graph (DAG) structure. The system performs breadth-first traversal of components while executing health checks asynchronously for better performance.

## Problem Statement

Develop a system that can:

1. Accept a JSON definition of system components and their dependencies in DAG form
2. Traverse the components in breadth-first order to maintain dependency relationships
3. Check component health asynchronously for better performance
4. Provide visual and tabular representation of system health
5. Handle component dependencies and validate DAG structure

## Solution Approach

### Architecture

- FastAPI for the web API
- Async health checks using Python's asyncio
- NetworkX for DAG validation and visualization
- Pydantic for data validation
- Rich for console output formatting

### Key Features

- BFS traversal with parallel health checks within each level
- Async component health checking for improved performance
- DAG validation to prevent cycles
- Visual graph representation with health status
- Comprehensive health status reporting

### Trade-offs and Design Decisions

1. **BFS vs DFS**

   - Chose BFS to check dependent components only after their dependencies
   - Allows parallel checking of components at the same level
   - Trade-off: Requires more memory to store level components

2. **Async Health Checks**

   - Parallel health checks within each BFS level
   - Better performance for components with similar dependencies
   - Trade-off: More complex error handling

3. **In-Memory Processing**

   - All processing done in memory for simplicity
   - Trade-off: Limited by available RAM for large systems

## Setup and Installation

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

### Option 1: Using the Example Script

```bash
cd examples
python run_health_check.py workflow_dag.json
```

### Option 2: Running the API Server

```bash
cd src
uvicorn system_health_checker.api.main:app --reload
```

## API Endpoints

### 1. Upload System Definition

- **Endpoint**: `POST /api/v1/upload-system`
- **Purpose**: Upload and validate system component definitions
- **Input**: JSON file with component definitions
- **Response**: Success message or validation errors

### 2. Check System Health

- **Endpoint**: `POST /api/v1/check-health`
- **Purpose**: Check health of all components
- **Input**: JSON file with component definitions
- **Response**:
  - Component health statuses
  - System health summary
  - Graph visualization (base64 encoded)

### 3. Health Check

- **Endpoint**: `GET /api/v1/health`
- **Purpose**: API health check
- **Response**: API status

## Example System Definition

```json
{
  "components": [
    {
      "id": "database",
      "name": "Database Service",
      "dependencies": []
    },
    {
      "id": "cache",
      "name": "Cache Service",
      "dependencies": ["database"]
    },
    {
      "id": "api",
      "name": "API Gateway",
      "dependencies": ["cache"]
    }
  ],
  "version": "1.0"
}
```

## Using curl

Check system health:

```bash
curl -X POST http://localhost:8000/api/v1/check-health \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/workflow_dag.json"
```

## Project Structure

```
system_health_checker/
├── api/
│   ├── main.py          # FastAPI application
│   └── routes.py        # API route definitions
├── core/
│   └── health_checker.py # Health checking logic
├── models/
│   └── component_health.py # Data models
└── utils/
    └── visualizer.py    # Graph visualization
```

## Testing

Run tests using pytest from the project root directory:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with print statements visible
pytest tests/ -s

# Run with coverage report
pytest tests/ --cov=system_health_checker

# Run with detailed coverage report
pytest tests/ --cov=system_health_checker --cov-report=term-missing

# Run specific test file
pytest tests/test_health_checker.py

# Run tests matching a pattern
pytest tests/ -k "health"

# Run and show test durations
pytest tests/ --durations=0
```

### Test Structure

Tests are organized following the AAA (Arrange, Act, Assert) pattern:

```python
def test_something():
    # Arrange - Set up test data
    component = HealthCheckComponent(id="test", name="Test")

    # Act - Perform the action
    result = perform_action(component)

    # Assert - Verify the results
    assert result.status == expected_status
```

### Test Files

- `test_models.py`: Tests for data models and DAG validation
- `test_health_checker.py`: Tests for health checking logic and BFS traversal
- `test_api.py`: Tests for API endpoints and request handling
- `test_visualizer.py`: Tests for graph visualization
- `conftest.py`: Shared test fixtures and configurations

### Coverage Requirements

The project maintains test coverage requirements:

- Minimum overall coverage: 80%
- Core functionality coverage: 90%
- Critical paths coverage: 100%

Run detailed coverage report:

```bash
pytest tests/ --cov=system_health_checker --cov-report=html
```

This generates an HTML coverage report in the `htmlcov` directory.

## Limitations

1. Simulated health checks (random status)
2. In-memory processing only
3. No persistent storage
4. No authentication/authorization
5. Limited to synchronous component dependencies

## Future Improvements

1. Real health check implementations
2. Persistent storage for health history
3. Authentication and authorization
4. Component health check customization
5. Real-time health monitoring
6. Webhook notifications for status changes
