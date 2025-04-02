import argparse
import asyncio
import sys
from pathlib import Path

import httpx
from rich.console import Console
from rich.table import Table

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

console = Console()


async def wait_for_server(url: str, timeout: int = 30, interval: float = 0.1) -> bool:
    """Wait for server to be ready."""
    async with httpx.AsyncClient() as client:
        start_time = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                response = await client.get(f"{url}/api/v1/health")
                if response.status_code == 200:
                    return True
            except httpx.RequestError:
                await asyncio.sleep(interval)
        return False


async def check_system_health(file_path: str) -> None:
    """
    Run a health check on the system defined in the JSON file.
    """
    try:
        # Validate the input file exists
        if not Path(file_path).exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            return

        # Start the FastAPI server
        import uvicorn

        from system_health_checker.api.main import app

        # Configure the server
        config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
        server = uvicorn.Server(config)

        # Start server in background
        server_task = asyncio.create_task(server.serve())

        # Wait for server to be ready
        server_url = "http://127.0.0.1:8000"
        if not await wait_for_server(server_url):
            console.print("[red]Error: Server failed to start[/red]")
            return

        # Make the health check request
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": ("system.json", f, "application/json")}
                response = await client.post(
                    f"{server_url}/api/v1/check-health", files=files
                )

                if response.status_code == 200:
                    result = response.json()

                    # Display the results in a table
                    table = Table(title="System Health Status")
                    table.add_column("Component", style="cyan")
                    table.add_column("Status", style="green")
                    table.add_column("Last Checked", style="yellow")

                    for component in result["components"]:
                        status = component["health_status"]
                        status_color = {"healthy": "green", "unhealthy": "red"}.get(
                            status, "yellow"
                        )

                        table.add_row(
                            component["name"],
                            f"[{status_color}]{status}[/{status_color}]",
                            component["last_checked"] or "Never",
                        )

                    console.print(table)

                    # Display summary
                    summary = result["summary"]
                    console.print("\n[bold]Summary:[/bold]")
                    console.print(f"Total Components: {summary['total_components']}")
                    console.print(f"Healthy: {summary['healthy_components']}")
                    console.print(f"Unhealthy: {summary['unhealthy_components']}")
                    console.print(f"Health %: {summary['health_percentage']:.1f}%")

                    # Save the graph image
                    if result.get("graph_image"):
                        graph_path = Path(file_path).stem + "_health_graph.png"
                        import base64

                        with open(graph_path, "wb") as f:
                            f.write(base64.b64decode(result["graph_image"]))
                        console.print(f"\nGraph saved to: {graph_path}")
                else:
                    console.print(f"[red]Error: {response.text}[/red]")

        # Shutdown the server gracefully
        server.should_exit = True
        await server_task

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise


def main():
    """Main entry point for the health check script."""
    parser = argparse.ArgumentParser(
        description="Check health of a system defined in a JSON file"
    )
    parser.add_argument(
        "file", type=str, help="Path to the JSON file containing system definition"
    )
    args = parser.parse_args()

    # Run the health check
    asyncio.run(check_system_health(args.file))


if __name__ == "__main__":
    main()

# python -m examples.run_health_check examples/system.json
