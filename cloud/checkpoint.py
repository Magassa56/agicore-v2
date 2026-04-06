from cloud.github_sync import git_save
from datetime import datetime

def checkpoint(system_state):
    """
    Auto-checkpoint intelligent AGIcore
    """
    message = f"AGIcore checkpoint {datetime.now()} | state: {system_state}"
    git_save(message)
