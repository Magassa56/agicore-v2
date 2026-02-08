# services/agicore_mcp/cognition_test_harness.py
import asyncio
import time
import logging
from statistics import quantiles
import os

# Import the code to be tested
from services.agicore_mcp.cognition import handle_alert, latency_records

# --- Test Harness Setup ---

# Configure logging to capture all relevant events for validation
log_file = "cognition_test.log"
# Clear previous log file
if os.path.exists(log_file):
    os.remove(log_file)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler() # Also print to console
    ]
)
logger = logging.getLogger("CognitionTestHarness")


async def run_storm(num_alerts: int = 200):
    """
    Executes a 'storm' of concurrent alert-handling tasks and returns the
    background tasks that were created.
    """
    logger.info(f"Starting alert storm with {num_alerts} concurrent requests.")
    # Fast-path tasks will complete quickly, background tasks will be returned
    fast_path_tasks = [handle_alert(i) for i in range(num_alerts)]
    background_tasks = await asyncio.gather(*fast_path_tasks)
    logger.info("Alert storm (fast-path) finished.")
    return background_tasks

def evaluate_results(num_alerts: int = 200):
    """
    Measures p99 latency and validates data integrity from logs.
    This is the core of the QA-Tester Agent's validation logic.
    """
    logger.info("Evaluating test results...")
    if not latency_records or len(latency_records) < num_alerts:
        logger.error(f"Integrity check failed: Expected {num_alerts} latency records, but found {len(latency_records)}.")
        return False, 0.0

    # Criterion 1: p99 latency
    p99 = quantiles(latency_records, n=100)[98]  # 99th percentile
    
    # Criterion 2: Success rate (all requests recorded)
    success_rate = len(latency_records) / num_alerts * 100
    
    logger.info(f"p99 latency: {p99*1000:.2f}ms | Success rate: {success_rate:.2f}%")
    
    # Criterion 3: Data integrity via logs
    try:
        with open(log_file, "r") as f:
            log_content = f.read()
        # Check that all background tasks completed
        all_background_tasks_logged = all(f"Alert {i}: background analysis completed." in log_content for i in range(num_alerts))
        if not all_background_tasks_logged:
            logger.error("Integrity check failed: Not all background analysis tasks completed and logged.")
    except FileNotFoundError:
        logger.error(f"Log file '{log_file}' not found for integrity check.")
        all_background_tasks_logged = False
        
    passed = all_background_tasks_logged and success_rate >= 100 and p99 <= 0.05
    return passed, p99

async def main_test_harness():
    """Entry point for the QA-Tester Agent."""
    num_alerts = 200
    
    # Phase 1: Run the storm and get the background tasks
    background_tasks = await run_storm(num_alerts)
    
    # Phase 2: Wait for all background analysis to complete
    logger.info(f"Waiting for {len(background_tasks)} background analysis tasks to complete...")
    await asyncio.gather(*background_tasks)
    logger.info("All background analysis tasks are complete.")

    # Phase 3: Now, evaluate the results
    passed, p99_latency = evaluate_results(num_alerts)
    
    if passed:
        logger.info("✅ TEST PASSED: Meta-SRE async routing criteria met.")
    else:
        logger.warning(f"🔥 TEST FAILED: Criteria not met (p99={p99_latency*1000:.2f}ms). Adjust architecture and retry.")

if __name__ == "__main__":
    asyncio.run(main_test_harness())
