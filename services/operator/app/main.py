import yaml
from pathlib import Path

def main():
    """
    Operator main entry point.
    """
    print("Hello from AGIcore Operator!")

    # Build a robust path to the state file from the project root
    state_file = Path(__file__).resolve().parent.parent.parent.parent / "ops" / "state" / "STATE.yml"

    if state_file.exists():
        print(f"Found state file at {state_file}, attempting to read...")
        try:
            with open(state_file, 'r') as f:
                state = yaml.safe_load(f)
            print("Successfully read state:")
            print(yaml.dump(state, indent=2))
        except Exception as e:
            print(f"Error reading or parsing state file: {e}")
    else:
        print(f"State file not found at {state_file}. Continuing without state.")

if __name__ == "__main__":
    main()
