import json
import os

current_working_directory = os.getcwd()
print(f"Directory di lavoro corrente: {current_working_directory}")

"""
from thelios.thelios_tools_extension.tools.queries import brand_query

config_path = r"thelios/thelios_tools_extension/settings/settings.json"

def load_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Errore: File di configurazione non trovato in {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Errore: File di configurazione non valido in {config_path}")
        return None

config = load_config(config_path)

if config:
    db_key = config["keys"]["db_key"]
    combo_elements = brand_query(db_key) 
    
print(combo_elements)
"""