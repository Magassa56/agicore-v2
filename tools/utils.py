
import logging
import sys
from functools import wraps
from pydantic import BaseModel
from typing import Optional

# --- Standardized Logging ---
def get_logger(name: str):
    """
    Returns a configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger

# --- Standardized Error Handling ---
class APIError(BaseModel):
    """A standard error response model."""
    detail: str
    code: Optional[str] = None

def handle_errors(func):
    """
    A decorator to catch exceptions and return a standardized error response.
    This is useful for wrapping tool functions or other business logic.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger = get_logger(func.__module__)
            logger.error(f"Error in '{func.__name__}': {str(e)}", exc_info=True)
            # In a real app, you might return a specific error structure
            return {
                "error": True,
                "message": f"An unexpected error occurred: {str(e)}",
                "function": func.__name__,
            }
    return wrapper

# Example of using the decorator
@handle_errors
async def potentially_failing_function():
    # This function might raise an error
    raise ValueError("This is a simulated failure.")

if __name__ == '__main__':
    # Example usage
    logger = get_logger(__name__)
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")

    async def run_example():
        result = await potentially_failing_function()
        print(result)
    
    import asyncio
    asyncio.run(run_example())
