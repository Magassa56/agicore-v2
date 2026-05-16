import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


def main():
    """
    Operator main entry point.
    """
    logging.basicConfig(level=logging.INFO)
    logger.info("AGIcore Operator starting")

    # Build a robust path to the state file from the project root
    state_file = Path(__file__).resolve().parent.parent.parent.parent / "ops" / "state" / "STATE.yml"

    if state_file.exists():
        logger.info("Found state file at %s, attempting to read...", state_file)
        try:
            with open(state_file, "r") as f:
                state = yaml.safe_load(f)
            logger.info("Successfully read state:\n%s", yaml.dump(state, indent=2))
        except Exception as e:
            logger.error("Error reading or parsing state file: %s", e)
    else:
        logger.info("State file not found at %s. Continuing without state.", state_file)

if __name__ == "__main__":
    main()
