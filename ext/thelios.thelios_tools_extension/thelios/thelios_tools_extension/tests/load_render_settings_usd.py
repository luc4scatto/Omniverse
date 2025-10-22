# load_render_settings_usd.py
# Eseguire in Script Editor di USD Composer / qualsiasi app Kit 108

from pxr import Usd, Sdf
import omni.usd
import carb
import os

def add_render_settings_sublayer(settings_usd_path: str, insert_on_top: bool = True) -> bool:
    """
    Aggiunge un file USD di render settings come sublayer allo stage corrente.
    - settings_usd_path: percorso assoluto (o omni://) del file RenderSettings.usd
    - insert_on_top: True = massima precedenza (sopra), False = bassa precedenza (in fondo)
    """
    ctx = omni.usd.get_context()
    stage = ctx.get_stage()
    if stage is None:
        carb.log_error("Nessuno stage aperto.")
        return False

    # Verifica percorso
    if not (settings_usd_path.startswith("omniverse://") or os.path.exists(settings_usd_path)):
        carb.log_error(f"Percorso non valido: {settings_usd_path}")
        return False

    root = stage.GetRootLayer()
    sublayers = list(root.subLayerPaths)

    # Evita duplicati
    if settings_usd_path in sublayers:
        carb.log_info("RenderSettings USD è già presente come sublayer.")
        return True

    if insert_on_top:
        sublayers.insert(0, settings_usd_path)
    else:
        sublayers.append(settings_usd_path)

    root.subLayerPaths = sublayers
    carb.log_info(f"Aggiunto sublayer: {settings_usd_path}")
    return True

# Esempio d’uso:
# Cambiare con il percorso reale, locale o Nucleus
settings_usd = r"C:\Projects\RenderSettings.usd"  # oppure "omniverse://server/Projects/RenderSettings.usd"
add_render_settings_sublayer(settings_usd, insert_on_top=True)
