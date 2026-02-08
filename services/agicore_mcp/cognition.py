# services/agicore_mcp/cognition.py
import asyncio
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)

# This module is designed to be the core asynchronous processing engine.
# The test harness will call these functions to validate performance.

# Queue to store latency records, accessible for monitoring
latency_records = deque(maxlen=1000)

async def heavy_analysis_task(alert_id: int):
    """
    Simulates a heavy, non-blocking background analysis task.
    In a real scenario, this could be a call to a model, a database query,
    or a complex computation.
    """
    await asyncio.sleep(2)  # Artificial 2s analysis
    logger.info(f"Alert {alert_id}: background analysis completed.")

async def handle_alert(alert_id: int):
    """
    Handles an incoming alert. The processing is split into a fast,
    non-blocking part and a long-running background task.
    """
    start = time.perf_counter()
    
    # Schedule the heavy analysis to run in the background without blocking.
    background_task = asyncio.create_task(heavy_analysis_task(alert_id))
    
    # Simulate the fast part of the processing (e.g., acknowledging the request).
    await asyncio.sleep(0.01)  # 10ms of lightweight processing
    end = time.perf_counter()
    
    # Record latency of the fast-path operation.
    latency = end - start
    latency_records.append(latency)
    logger.info(f"Alert {alert_id}: routing handled in {latency*1000:.2f}ms.")
    
    # Return the background task so the caller can wait for it if needed
    return background_task
