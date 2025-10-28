import json
from pathlib import Path

SETTINGS_PATH = Path(__file__).parent.joinpath("settings")
json_path = f"{SETTINGS_PATH}\\settings.json"

def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid configuration file at {config_path}")
        return None