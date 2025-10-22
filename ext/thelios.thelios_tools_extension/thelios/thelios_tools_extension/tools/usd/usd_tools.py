"""
USD Hierarchy and Payload Management Script for NVIDIA Omniverse

This script provides utilities for creating hierarchical USD structures and managing
payload imports in NVIDIA Omniverse. It includes functionality for:
- Creating standardized USD scene hierarchies
- Validating USD file existence (local and Omniverse paths)
- Importing payloads with proper error handling and user notifications
- Managing USD prims and transforms

Dependencies:
    - omni.usd: Omniverse USD context management
    - omni.kit.commands: Omniverse Kit command execution
    - omni.kit.app: Omniverse application interface
    - pxr: Pixar USD Python bindings
    - omni.kit.notification_manager: User notification system
    - os: Operating system interface for file operations

Author: [Luca Scattolin - Thelios]
Version: 1.0
Date: [Current Date]
"""

import omni.usd
import omni.kit.commands
import omni.kit.app
from pxr import Usd, UsdGeom, Sdf
from omni.kit.notification_manager import post_notification, NotificationStatus
import os


def create_hierarchy_structure(stage: Usd.Stage, model_name: str, sku_name: str, release: str) -> None:
    """
    Create a standardized USD hierarchy structure for product models.
    
    This function creates a predefined hierarchy structure following the pattern:
    /World/Models/glass_Xform/{model_name}_Xform/Release_{release}/{model_name}_{sku_name}
    
    Args:
        stage (Usd.Stage): The USD stage where the hierarchy will be created
        model_name (str): Name of the model used in the hierarchy paths
        sku_name (str): SKU identifier for the specific product variant
        release (str): Release version identifier
        
    Returns:
        None
        
    Example:
        >>> stage = omni.usd.get_context().get_stage()
        >>> create_hierarchy_structure(stage, "Chair", "001", "v1.0")
        # Creates: /World/Models/glass_Xform/Chair_Xform/Release_v1.0/Chair_001
    """
    
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
    
    # 0. Create/get World as root and defaultPrim
    world_path = "/World"
    world_xform = get_or_create_xform(stage, world_path)
    
    # Set World as the stage's defaultPrim
    stage.SetDefaultPrim(world_xform.GetPrim())
    
    # 1. Create Models (Scope) under World
    models_path = f"{world_path}/Models"
    models_scope = get_or_create_scope(stage, models_path)
    
    # 2. Create glass_Xform (Xform) under Models
    glass_xform_path = f"{models_path}/glass_Xform"
    glass_xform = get_or_create_xform(stage, glass_xform_path)
    
    # Apply 45° rotation animation on Y axis to glass_Xform ---------
    
    prim = stage.GetPrimAtPath(glass_xform_path)
    xformable = UsdGeom.Xformable(prim)
    rotY = xformable.GetRotateYOp()
    if not rotY:
        rotY = xformable.AddRotateYOp(UsdGeom.XformOp.PrecisionFloat)
        
    for i in range(1, 9):  # 8 frame
        angle = -45.0 * i
        rotY.Set(angle, Usd.TimeCode(i))    
    # ---------------------------------------------------------------        
    
    # 3. Create model_name_Xform (Xform) under glass_Xform
    model_xform_path = f"{glass_xform_path}/{model_name}_Xform"
    model_xform = get_or_create_xform(stage, model_xform_path)
    
    # 4. Create Release (Scope) under model_name_Xform
    release_scope_path = f"{model_xform_path}/Release_{release}"
    release_scope = get_or_create_scope(stage, release_scope_path)
    
    # 5. Create SKU scope with underscore to avoid path errors
    sku_scope_path = f"{release_scope_path}/{model_name}_{str(sku_name)}"
    sku_scope = get_or_create_scope(stage, sku_scope_path)

def check_usd_file_exists(file_path: str) -> bool:
    """
    Check if a USD file exists at the specified path.
    Supports both local file paths and Omniverse URLs.
    
    This function can validate USD files in two contexts:
    - Local filesystem paths: Uses standard os.path operations
    - Omniverse URLs (omniverse://): Attempts to open the USD stage
    
    Args:
        file_path (str): Path to the USD file to check. Can be a local path
                        or an Omniverse URL (starting with "omniverse://")
                        
    Returns:
        bool: True if the file exists and is accessible, False otherwise
        
    Example:
        >>> check_usd_file_exists("/path/to/model.usd")
        True
        >>> check_usd_file_exists("omniverse://server/path/model.usd")
        False
    """
    if file_path.startswith("omniverse://"):
        # For Omniverse paths, use Usd.Stage.Open to verify existence
        try:
            temp_stage = Usd.Stage.Open(file_path)
            if temp_stage:
                return True
            else:
                return False
        except Exception:
            return False
    else:
        # For local paths, use os.path.exists
        return os.path.exists(file_path) and os.path.isfile(file_path)

def assign_payload(target_path: str, payload_asset_path: str) -> Usd.Prim:
    """
    Assign a payload to a prim while preserving existing children.
    Does not handle nested payloads - lets them load normally.
    
    This function attaches a USD payload to a specified prim in the current stage.
    Payloads are references to external USD files that can be loaded on-demand
    to improve performance with large scenes.
    
    Args:
        target_path (str): USD path where the payload should be attached
        payload_asset_path (str): Path to the USD file to be used as payload
        
    Returns:
        Usd.Prim: The prim that received the payload
        
    Raises:
        RuntimeError: If no active USD stage is found
        
    Example:
        >>> target_prim = assign_payload(
        ...     "/World/Models/Chair", 
        ...     "/path/to/chair_model.usd"
        ... )
    """
    
    context = omni.usd.get_context()
    stage = context.get_stage()
    
    if not stage:
        raise RuntimeError("No active stage found")
    
    # Find or create the target prim
    target_prim = _get_or_create_prim(stage, target_path)
    
    # Add the payload directly to the prim
    omni.kit.commands.execute("AddPayload",
        stage=stage,
        prim_path=target_prim.GetPath(),
        payload=Sdf.Payload(assetPath=payload_asset_path)
    )
    
    print(f"Payload added to: {target_prim.GetPath()}")
    
    # Load all payloads normally (no special handling for nested ones)
    stage.SetLoadRules(Usd.StageLoadRules.LoadAll())
    
    return target_prim

def _get_or_create_prim(stage: Usd.Stage, path: str) -> Usd.Prim:
    """
    Find an existing prim or create the hierarchy if necessary.
    
    This is a helper function that first searches for a prim by name
    throughout the stage. If not found, it creates the complete path
    hierarchy using appropriate prim types (Xform for transforms, 
    Scope for organization).
    
    Args:
        stage (Usd.Stage): The USD stage to search in
        path (str): The full USD path to find or create
        
    Returns:
        Usd.Prim: The found or newly created prim
        
    Note:
        This function uses naming conventions to determine prim types:
        - Prims containing "_Xform" or named "World" become UsdGeom.Xform
        - All other prims become UsdGeom.Scope
    """
    
    # First search by name
    prim_name = path.split("/")[-1]
    for prim in stage.Traverse():
        if prim.GetName() == prim_name:
            return prim
    
    # If not found, create the hierarchy
    path_parts = path.strip("/").split("/")
    current_path = "/"
    
    for part in path_parts:
        if not part:
            continue
        current_path = f"{current_path.rstrip('/')}/{part}"
        sdf_path = Sdf.Path(current_path)
        
        if not stage.GetPrimAtPath(sdf_path).IsValid():
            if "_Xform" in part or part == "World":
                UsdGeom.Xform.Define(stage, sdf_path)
            else:
                UsdGeom.Scope.Define(stage, sdf_path)
    
    return stage.GetPrimAtPath(Sdf.Path(path))

def import_payload(payload_usd_path: str, target_path: str) -> None:
    """
    Import a USD payload after verifying the file exists.
    Shows user notifications for success and error states.
    
    This is the main entry point for payload import operations. It performs
    validation, executes the import, and provides user feedback through
    the Omniverse notification system.
    
    Args:
        payload_usd_path (str): Path to the USD file to import as payload.
                                Can be local path or Omniverse URL
        target_path (str): USD path where the payload should be attached
        
    Returns:
        None
        
    Notifications:
        - Warning notification if file doesn't exist (10 seconds)
        - Info notification on successful import (5 seconds)  
        - Warning notification on import error (10 seconds)
        
    Example:
        >>> import_payload(
        ...     "/path/to/model.usd",
        ...     "/World/Models/MyModel"
        ... )
        # Shows success notification and prints "Import completed"
    """
    
    # Check if the USD file exists
    if not check_usd_file_exists(payload_usd_path):
        # Show error alert
        post_notification(
            f"ERROR: USD file not found: {payload_usd_path}",
            duration=10,
            status=NotificationStatus.WARNING
        )
        print(f"Error: USD file not found at: {payload_usd_path}")
        return
    
    try:
        assign_payload(
            target_path=target_path,
            payload_asset_path=payload_usd_path
        )
        
        # Success notification
        post_notification(
            "Payload successfully imported",
            duration=5,
            status=NotificationStatus.INFO
        )
        print("Import completed")
        
    except Exception as e:
        # Error notification during import
        post_notification(
            f"ERROR during import: {str(e)}",
            duration=10,
            status=NotificationStatus.WARNING
        )
        print(f"Error: {e}")
