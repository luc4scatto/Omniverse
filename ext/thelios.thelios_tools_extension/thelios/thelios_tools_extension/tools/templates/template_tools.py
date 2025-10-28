from thelios.thelios_tools_extension.tools.usd import usd_tools
from pxr import Usd, UsdGeom, Sdf
import omni.kit.app
import carb
import os

world_path = "/World"
camera_target = f"/World/Setup/Cameras"
light_target = f"/World/Setup/Lights"
limbo_target = f"/World/Setup/Limbo"

def get_or_create_scope(stage: Usd.Stage, path: str) -> UsdGeom.Scope:
        """
        Check if a Scope exists, otherwise create it.
        
        Args:
            stage (Usd.Stage): The USD stage
            path (str): Path where the Scope should exist or be created
            
        Returns:
            UsdGeom.Scope: The existing or newly created Scope
        """
        prim = stage.GetPrimAtPath(path)
        if prim.IsValid():
            return UsdGeom.Scope(prim)
        else:
            return UsdGeom.Scope.Define(stage, path)
    
def get_or_create_xform(stage: Usd.Stage, path: str) -> UsdGeom.Xform:
    """
    Check if an Xform exists, otherwise create it.
    
    Args:
        stage (Usd.Stage): The USD stage
        path (str): Path where the Xform should exist or be created
        
    Returns:
        UsdGeom.Xform: The existing or newly created Xform
    """
    prim = stage.GetPrimAtPath(path)
    if prim.IsValid():
        return UsdGeom.Xform(prim)
    else:
        return UsdGeom.Xform.Define(stage, path)

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

def _default_prim_set(stage: Usd.Stage):
    
    world_xform = get_or_create_xform(stage, world_path)
    # Set World as the stage's defaultPrim
    stage.SetDefaultPrim(world_xform.GetPrim())
    
    setup_path = f"{world_path}/Setup"
    setup_scope = get_or_create_scope(stage, setup_path)

def _import_camera(stage: Usd.Stage, brand_camera_model: str, combo_elements: list, templates_dir: str):
    _default_prim_set(stage)
    
    brand_camera_index = brand_camera_model.as_int
    brand_camera_value = combo_elements[brand_camera_index]
    brand_camera = brand_camera_value.replace(" ", "_")
    
    camera_payload = f"{templates_dir}\\ABC\\camera\\{brand_camera}_cam.usd"
    print(camera_payload)
    
    camera_xform = get_or_create_xform(stage, camera_target)
    usd_tools.import_payload(camera_payload, camera_target)
    
def _import_lights(stage: Usd.Stage, templates_dir: str):
    _default_prim_set(stage)
    
    light_payload = f"{templates_dir}/ABC/lights.usd"
    
    lights_xform = get_or_create_scope(stage, light_target)
    usd_tools.import_payload(light_payload, light_target)
    
def _import_limbo(stage: Usd.Stage, templates_dir: str):
    _default_prim_set(stage)
    limbo_xform = get_or_create_xform(stage, limbo_target)
    limbo_payload = f"{templates_dir}/ABC/limbo.usd"
    
    usd_tools.import_payload(limbo_payload, limbo_target)

def _import_settings(stage: Usd.Stage, templates_dir: str):
    #_default_prim_set(stage)
    print(f"Importing Settings... {templates_dir}")
    #add_render_settings_sublayer(settings_path, insert_on_top=True)