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
from pxr import Usd, UsdGeom, Sdf, UsdShade
import os
from ... import constants
from .alerts import AlertWindow

class USDTools():
    
    def __init__(self):
        self.alert_instance = AlertWindow()
    
    def create_hierarchy_structure(self, stage: Usd.Stage, model_name: str, sku_name: str, release: str) -> None:
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
        _stage = omni.usd.get_context().get_stage()
        
        def get_or_create_scope(stage: Usd.Stage, path: str) -> UsdGeom.Scope:
            """
            Check if a Scope exists, otherwise create it.
            
            Args:
                stage (Usd.Stage): The USD stage
                path (str): Path where the Scope should exist or be created
                
            Returns:
                UsdGeom.Scope: The existing or newly created Scope
            """
            prim = _stage.GetPrimAtPath(path)
            if prim.IsValid():
                return UsdGeom.Scope(prim)
            else:
                return UsdGeom.Scope.Define(_stage, path)
        
        def get_or_create_xform(stage: Usd.Stage, path: str) -> UsdGeom.Xform:
            """
            Check if an Xform exists, otherwise create it.
            
            Args:
                stage (Usd.Stage): The USD stage
                path (str): Path where the Xform should exist or be created
                
            Returns:
                UsdGeom.Xform: The existing or newly created Xform
            """
            prim = _stage.GetPrimAtPath(path)
            if prim.IsValid():
                return UsdGeom.Xform(prim)
            else:
                return UsdGeom.Xform.Define(_stage, path)
        
        # 0. Create/get World as root and defaultPrim
        world_path = "/World"
        world_xform = get_or_create_xform(_stage, world_path)
        
        # Set World as the stage's defaultPrim
        _stage.SetDefaultPrim(world_xform.GetPrim())
        
        # 1. Create Models (Scope) under World
        models_path = f"{world_path}/Models"
        models_scope = get_or_create_scope(_stage, models_path)
        
        # 2. Create glass_Xform (Xform) under Models
        glass_xform_path = f"{models_path}/glass_Xform"
        glass_xform = get_or_create_xform(_stage, glass_xform_path)
        
        # Apply 45° rotation animation on Y axis to glass_Xform ---------
        
        prim = _stage.GetPrimAtPath(glass_xform_path)
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
        model_xform = get_or_create_xform(_stage, model_xform_path)
        
        # 4. Create Release (Scope) under model_name_Xform
        release_scope_path = f"{model_xform_path}/Release_{release}"
        release_scope = get_or_create_scope(_stage, release_scope_path)
        
        # 5. Create SKU scope with underscore to avoid path errors
        sku_scope_path = f"{release_scope_path}/{model_name}_{str(sku_name)}"
        sku_scope = get_or_create_scope(_stage, sku_scope_path)

    def check_usd_file_exists(self, file_path: str) -> bool:
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

    def assign_payload(self, target_path: str, payload_asset_path: str) -> Usd.Prim:
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
        target_prim = self._get_or_create_prim(stage, target_path)
        
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

    def _get_or_create_prim(self, stage: Usd.Stage, path: str) -> Usd.Prim:
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
        _stage = omni.usd.get_context().get_stage()
        # First search by name
        prim_name = path.split("/")[-1]
        for prim in _stage.Traverse():
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
            
            if not _stage.GetPrimAtPath(sdf_path).IsValid():
                if "_Xform" in part or part == "World":
                    UsdGeom.Xform.Define(_stage, sdf_path)
                else:
                    UsdGeom.Scope.Define(_stage, sdf_path)
        
        return _stage.GetPrimAtPath(Sdf.Path(path))

    def import_payload(self, payload_usd_path: str, target_path: str) -> None:
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
        if not self.check_usd_file_exists(payload_usd_path):
            # Show error alert
            self.alert_instance.post_notification_warning(f"ERROR: USD file not found: {payload_usd_path}")
            
            print(f"Error: USD file not found at: {payload_usd_path}")
            return
        
        try:
            self.assign_payload(
                target_path=target_path,
                payload_asset_path=payload_usd_path
            )
            
            print("Payload import completed successfully.")
            
        except Exception as e:
            # Error notification during import
            self.alert_instance.post_notification_warning(f"ERROR during import: {str(e)}")
            print(f"Error: {e}")
        
    def get_filtered_scopes(self) -> list[str]:
        
        _stage = omni.usd.get_context().get_stage()
        
        scopes = [
            prim.GetPath().pathString
            for prim in _stage.Traverse()
            if prim.GetTypeName() == "Scope"
            and prim.GetPath().pathString.startswith("/World/Models")
            and not prim.GetName().endswith(("Looks", "mtl"))
            and prim.IsLoaded()
        ]
        
        filtered = [
            s for s in scopes
            if not s.split("/")[-1].startswith("Release_") 
            and len(s.split("/")) <= 7
        ]
        
        final_list = [s.split("/")[-1] for s in filtered][1:] 
        
        return final_list

    # -------------------------------------------------------------------------

    def find_scope_by_name(self, stage, scope_name):
        
        #Find a scope by name in the entire stage hierarchy.
        
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Scope) and prim.GetName() == scope_name:
                return prim
        return None

    def is_descendant_of(self, prim, ancestor):
        #Check if a prim is a descendant (child, grandchild, etc.) of another prim.
        
        current = prim.GetParent()
        while current and current.GetPath() != "/":
            if current.GetPath() == ancestor.GetPath():
                return True
            current = current.GetParent()
        return False

    def set_visibility(self, prim, visible):
        
        #Explicitly set the visibility of a prim.
        
        imageable = UsdGeom.Imageable(prim)
        
        if not imageable:
            return
        
        vis_attr = imageable.GetVisibilityAttr()
        
        if not vis_attr:
            vis_attr = imageable.CreateVisibilityAttr()
        
        if visible:
            vis_attr.Set(UsdGeom.Tokens.inherited)
        else:
            vis_attr.Set(UsdGeom.Tokens.invisible)

    def make_parents_visible(self,prim):
        """
        Make all parent prims visible up to the root.
        This ensures visibility is not blocked by invisible parents.
        """
        parent = prim.GetParent()
        while parent and parent.GetPath() != "/":
            if UsdGeom.Imageable(parent):
                self.set_visibility(parent, True)
                #print(f"  ↑ Making parent visible: '{parent.GetName()}'")
            parent = parent.GetParent()

    def make_children_visible(self, parent_prim):
        
        #Recursively make all child prims visible.
        
        for child in parent_prim.GetAllChildren():
            if UsdGeom.Imageable(child):
                self.set_visibility(child, True)
                self.make_children_visible(child)

    def hide_all_scopes_except(self, target_scope_name, keep_scopes=None):
        """
        Hide all scopes except the specified one and those in the exceptions list.
        Also keeps all descendants (children) of the target scope visible.
        
        Args:
            target_scope_name (str): Name of the scope to keep visible (e.g., "CD40153U_32P")
            keep_scopes (list): List of scope names to keep visible 
                                Default: ["Models", "Setup", "Lights", "Cameras"]
        """
        # Default: keep common setup scopes visible
        if keep_scopes is None:
            keep_scopes = constants.SCOPES_TO_KEEP
        
        stage = omni.usd.get_context().get_stage()
        
        if not stage:
            print("Error: No active stage")
            return
        
        # Find the target scope
        target_scope_prim = self.find_scope_by_name(stage, target_scope_name)
        
        if not target_scope_prim:
            print(f"⚠ ERROR: Scope '{target_scope_name}' not found!")
            return
        
        #print(f"\n✓ Found target scope: '{target_scope_name}'")
        #print(f"  Path: {target_scope_prim.GetPath()}")
        
        # Find all scopes to keep visible
        keep_scope_prims = {}
        for scope_name in keep_scopes:
            scope_prim = self.find_scope_by_name(stage, scope_name)
            if scope_prim:
                keep_scope_prims[scope_name] = scope_prim
                #print(f"✓ Scope to keep: '{scope_name}' - {scope_prim.GetPath()}")
            #else:
                #print(f"⚠ Scope '{scope_name}' not found (will be ignored)")
        """
        print("\n" + "="*60)
        print("VISIBILITY MODIFICATION:")
        print("="*60)
        """
        
        hidden_count = 0
        visible_count = 0
        hidden_scopes = []
        visible_scopes = []
        
        # Process all scopes
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Scope):
                prim_name = prim.GetName()
                prim_path = prim.GetPath()
                
                # Target scope: visible
                if prim_path == target_scope_prim.GetPath():
                    #print(f"\n✓ TARGET: '{prim_name}' → VISIBLE")
                    self.set_visibility(prim, True)
                    self.make_children_visible(prim)
                    visible_count += 1
                    visible_scopes.append(prim_name)
                    
                # Child/descendant of target scope: visible
                elif self.is_descendant_of(prim, target_scope_prim):
                    #print(f"✓ CHILD OF TARGET: '{prim_name}' → VISIBLE")
                    self.set_visibility(prim, True)
                    self.make_children_visible(prim)
                    visible_count += 1
                    visible_scopes.append(prim_name)
                    
                # Scopes in the exceptions list: visible (but NOT their children)
                elif prim_name in keep_scope_prims and prim_path == keep_scope_prims[prim_name].GetPath():
                    #print(f"✓ EXCEPTION: '{prim_name}' → VISIBLE")
                    self.set_visibility(prim, True)
                    # NOTE: We make children visible here too, but they will be handled individually
                    self.make_children_visible(prim)
                    visible_count += 1
                    visible_scopes.append(prim_name)
                    
                # Other scopes: hide
                else:
                    #print(f"○ '{prim_name}' → HIDDEN")
                    self.set_visibility(prim, False)
                    hidden_count += 1
                    hidden_scopes.append(prim_name)
        """
        # Make all parents of target scope visible
        print("\n" + "="*60)
        #print("MAKING PARENT CHAIN VISIBLE:")
        print("="*60)
        """
        
        self.make_parents_visible(target_scope_prim)
        
        # Also make parents of exception scopes visible
        for scope_name, scope_prim in keep_scope_prims.items():
            #print(f"\nMaking parent chain visible for '{scope_name}':")
            self.make_parents_visible(scope_prim)
        
        """
        # Summary
        print("\n" + "="*60)
        print(f"✓ OPERATION COMPLETED")
        print(f"\n  VISIBLE ({visible_count}):")
        for name in visible_scopes:
            print(f"    • {name}")
        print(f"\n  HIDDEN ({hidden_count}):")
        for name in hidden_scopes:
            print(f"    • {name}")
        print("="*60)
        """
        
    def get_create_looks(self):
        stage = omni.usd.get_context().get_stage()
        
        # controlla/crea /World se manca
        world_prim = stage.GetPrimAtPath("/World")
        if not world_prim:
            world_prim = stage.DefinePrim("/World", "Xform")
        
        # controlla/crea /World/Looks come Scope
        looks_prim = stage.GetPrimAtPath(constants.MATERIAL_TARGET)
        if not looks_prim:
            looks_prim = stage.DefinePrim(constants.MATERIAL_TARGET, "Scope")
        
    def get_materials_in_looks_scope(self, stage: Usd.Stage, looks_path=constants.MATERIAL_TARGET):
        looks_prim = stage.GetPrimAtPath(looks_path)
        if not looks_prim or not looks_prim.IsValid():
            print(f"Scope Looks non trovato a {looks_path}")
            return []
        
        materials = []
        for prim in Usd.PrimRange(looks_prim, Usd.TraverseInstanceProxies()):
            # Considera solo i prim che sono UsdShade.Material
            if prim.IsA(UsdShade.Material):
                materials.append(prim)
                
        return materials

    def print_looks_materials(self):
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()
        if not stage:
            print("Nessuno stage attivo")
            return
        
        mats = self.get_materials_in_looks_scope(stage, constants.MATERIAL_TARGET)
        print(f"Trovati {len(mats)} materiali sotto /World/Looks:")
        for p in mats:
            print(" -", p.GetPath())
        
    def ensure_looks_scope(self, stage, looks_path=constants.MATERIAL_TARGET):
        looks_prim = stage.GetPrimAtPath(looks_path)
        if not looks_prim or not looks_prim.IsValid():
            # Crea uno Scope/Xform per i materiali
            looks_prim = UsdGeom.Scope.Define(stage, Sdf.Path(looks_path)).GetPrim()
        return looks_prim

    def create_reference_under_parent( self,
        asset_usd_path: str,
        prim_in_file: str = "",         # es: "/Looks/Carpaint_Metallic_06" oppure "" per defaultPrim
        parent_path: str = constants.MATERIAL_TARGET,
        local_name: str = "ImportedRef"      # nome del prim figlio dentro /World/Looks
    ):
        ctx = omni.usd.get_context()
        stage = ctx.get_stage()

        # Assicurati che esista lo scope Looks
        self.ensure_looks_scope(stage, parent_path)

        # Path finale del prim referenziato, figlio di /World/Looks
        target_prim_path = f"{parent_path}/{local_name}"

        omni.kit.commands.execute(
            "CreateReference",
            usd_context=ctx,
            path_to=Sdf.Path(target_prim_path),
            asset_path=asset_usd_path,
            prim_path=Sdf.Path(prim_in_file) if prim_in_file else Sdf.Path.emptyPath
        )

        print(f"Reference created under {parent_path}: {target_prim_path} -> {asset_usd_path}")
        self.alert_instance.post_notification_info(f"INFO: reference imported: {local_name}")

    def save_material_overrides_to_source(self, material_path: str):

        stage = omni.usd.get_context().get_stage()
        mtl_prim = stage.GetPrimAtPath(material_path)
        
        if not mtl_prim.IsValid():
            print(f"Materiale non trovato: {material_path}")
            return
        
        source_file_path = self.get_reference_source_file(mtl_prim)
        if not source_file_path:
            self.alert_instance.post_notification_warning(f"ERROR: no referenced .usda file found")
            print("no referenced .usda file found")
            return
        
        print(f"File sorgente AUTO-RILEVATO: {source_file_path}")
        
        # 1. Apri il file originale
        source_stage = Usd.Stage.Open(source_file_path)
        if not source_stage:
            self.alert_instance.post_notification_warning(f"ERROR: source file not found")
            print(f"ERROR: source file not found")
            return
        
        # 2. Trova il materiale nel file originale (defaultPrim o /Red_MI)
        source_mtl_path = source_stage.GetDefaultPrim().GetPath() if source_stage.HasDefaultPrim() else "/Red_MI"
        source_mtl = source_stage.GetPrimAtPath(source_mtl_path)
        
        if not source_mtl.IsValid():
            print(f"Materiale '{source_mtl_path}' non trovato nel file")
            return
        
        # 3. COPIA TUTTI i parametri modificati
        modified_count = 0
        for attr in mtl_prim.GetAttributes():
            if attr.IsValid() and attr.HasAuthoredValueOpinion():
                source_attr = source_mtl.GetAttribute(attr.GetName())
                if source_attr.IsValid():
                    source_attr.Set(attr.Get())
                    print(f"{attr.GetName()} = {attr.Get()}")
                    modified_count += 1
        
        # 4. Salva
        source_stage.GetRootLayer().Save()
        self.alert_instance.post_notification_info(f"INFO: material updated: {source_file_path}")
        print(f"Saved! {modified_count} params updated → {source_file_path}")
        
    def get_reference_source_file(self, prim):
        
        # Scorri la PrimStack per trovare file .usda referenziati
        for prim_spec in prim.GetPrimStack():
            layer = prim_spec.layer
            if layer and layer.identifier.endswith('.usda') and os.path.exists(layer.identifier):
                return layer.identifier
            
            # Controlla anche references/payloads nella stack
            if hasattr(prim_spec, 'referenceList'):
                for ref in getattr(prim_spec.referenceList, 'prependedItems', []):
                    asset_path = ref.assetPath
                    if asset_path and asset_path.endswith('.usda') and os.path.exists(asset_path):
                        return asset_path
        
        # Fallback: subLayers del prim
        sub_layers = prim.GetAttribute("subLayers")
        if sub_layers.IsValid():
            paths = sub_layers.Get()
            for path in paths or []:
                if os.path.exists(path) and path.endswith('.usda'):
                    return path
        
        return None    