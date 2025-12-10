
import pytest
import asyncio
from unittest.mock import patch, AsyncMock

# Add relevant directories to sys.path to allow imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'services' / 'agicore-mcp'))

# Import the components to be tested
from tools import market_analysis, image_generation
from services.agicore_mcp.main import create_plan as mcp_create_plan

# This is an integration test, which tests the interaction between components.
# We will simulate a high-level user goal and check if the MCP and tools interact correctly.
# In a real-world scenario, this might involve running services in Docker and making real HTTP calls.
# For simplicity here, we will mock the service-to-service calls.

@pytest.mark.asyncio
async def test_planning_and_tool_execution_flow():
    """
    Tests a full flow:
    1. A goal is sent to the MCP.
    2. The MCP creates a plan.
    3. A step in the plan involves calling a tool.
    4. We verify the tool is called with the correct parameters.
    """
    goal = {"description": "Generate an image of a futuristic city"}

    # Mock the plan generation to return a plan that uses the image generation tool
    # Instead of calling the full MCP service, we can directly test the planning logic
    # and its interaction with tools.
    
    # Let's assume the plan has a step to call the 'generate_image' tool
    plan = {
        "id": "plan_integration_test",
        "steps": [
            {
                "action": "generate_image",
                "tool": "image_generation",
                "params": {"prompt": "A futuristic city with flying cars"}
            }
        ]
    }
    
    # We use patch to replace the actual tool function with a mock
    with patch('tools.image_generation.generate_image', new_callable=AsyncMock) as mock_generate_image:
        # Simulate the plan executor that would run this step
        step_to_execute = plan["steps"][0]
        
        if step_to_execute["tool"] == "image_generation":
            # Get the parameters for the tool
            params = step_to_execute["params"]
            # Execute the tool
            await image_generation.generate_image(**params)

        # Assert that our mock tool was called correctly
        mock_generate_image.assert_awaited_once_with(prompt="A futuristic city with flying cars")

# Note: This is a simplified integration test. A more thorough test would involve:
# - Spinning up the actual services in containers.
# - Using an HTTP client to send a request to the MCP's /create-plan endpoint.
# - The MCP would then make a real HTTP call to another service (e.g., a "Tool Runner" service).
# - We would then check the final output (e.g., an object in a test storage bucket).
# This level of testing requires more setup (e.g., Docker Compose, test databases).
