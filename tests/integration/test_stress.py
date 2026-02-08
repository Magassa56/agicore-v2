
import asyncio
import httpx
import time
import logging
from typing import List
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Test Configuration ---
BASE_URL = "http://localhost:8001"  # Assuming MCP runs on port 8001
MCP_CREATE_PLAN_URL = f"{BASE_URL}/create-plan"
MCP_EXECUTE_SYNC_URL = f"{BASE_URL}/execute-plan"
MCP_EXECUTE_BG_URL = f"{BASE_URL}/execute-plan-background"

# Load Test Parameters
CONCURRENT_REQUESTS = 200
HEAVY_TASK_SIMULATION_URL = MCP_EXECUTE_BG_URL 
LIGHT_REQUEST_URL = f"{BASE_URL}/" # The root endpoint is very lightweight

# --- Test Harness ---

@pytest.mark.asyncio
async def test_system_under_load():
    """
    Simulates a high-traffic scenario with a mix of light and heavy requests
    to test latency, throughput, and reliability.
    """
    latencies = []
    errors = 0

    async with httpx.AsyncClient() as client:
        # --- Step 1: Create a plan to be used by the test ---
        try:
            goal_payload = {"description": "stress test goal"}
            response = await client.post(MCP_CREATE_PLAN_URL, json=goal_payload, timeout=10)
            response.raise_for_status()
            plan_id = response.json()["id"]
            logger.info(f"Successfully created plan {plan_id} for stress test.")
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            pytest.fail(f"Failed to create initial plan for test: {e}")

        # --- Step 2: Define the tasks for concurrent execution ---
        # A mix of heavy background tasks and light, fast requests
        tasks = []
        
        # One heavy task
        heavy_task_url = f"{HEAVY_TASK_SIMULATION_URL}/{plan_id}"
        tasks.append(client.post(heavy_task_url))
        logger.info("Scheduled 1 heavy background task.")

        # Multiple light tasks
        for i in range(CONCURRENT_REQUESTS - 1):
            tasks.append(client.get(LIGHT_REQUEST_URL))
        logger.info(f"Scheduled {CONCURRENT_REQUESTS - 1} light requests.")

        # --- Step 3: Execute tasks concurrently and measure ---
        logger.info(f"--- Starting Concurrent Execution of {len(tasks)} tasks ---")
        start_time = time.time()
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        logger.info(f"--- Finished Concurrent Execution in {total_duration:.2f}s ---")

        # --- Step 4: Analyze results ---
        for i, res in enumerate(responses):
            if isinstance(res, Exception):
                logger.error(f"Request {i} failed: {res}")
                errors += 1
            elif res.status_code >= 400:
                logger.error(f"Request {i} returned error status: {res.status_code} | Response: {res.text}")
                errors += 1
                latencies.append(res.elapsed.total_seconds() * 1000) # in ms
            else:
                latencies.append(res.elapsed.total_seconds() * 1000) # in ms
        
        # --- Step 5: Assert performance criteria ---
        assert errors == 0, f"Encountered {errors} errors during the stress test."
        
        latencies.sort()
        p99_latency = latencies[int(len(latencies) * 0.99) -1]
        
        logger.info(f"Total requests: {len(latencies)}")
        logger.info(f"Success rate: {100 * (len(latencies) - errors) / len(latencies):.2f}%")
        logger.info(f"Min latency: {min(latencies):.2f} ms")
        logger.info(f"Max latency: {max(latencies):.2f} ms")
        logger.info(f"Average latency: {sum(latencies) / len(latencies):.2f} ms")
        logger.info(f"p99 latency: {p99_latency:.2f} ms")
        
        assert p99_latency < 50, f"p99 latency ({p99_latency:.2f}ms) exceeds the 50ms threshold."

        # Verification of the background task is tricky.
        # In a real system, we'd check logs, a database, or a monitoring system
        # to confirm the heavy task completed. For now, we trust FastAPI's BackgroundTasks.
        logger.info("Test assumes background task was handled by FastAPI correctly.")
