from pxr import Usd, UsdGeom
import omni.usd


def find_scope_by_name(stage, scope_name):
    
    #Find a scope by name in the entire stage hierarchy.
    
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Scope) and prim.GetName() == scope_name:
            return prim
    return None


def is_descendant_of(prim, ancestor):
    #Check if a prim is a descendant (child, grandchild, etc.) of another prim.
    
    current = prim.GetParent()
    while current and current.GetPath() != "/":
        if current.GetPath() == ancestor.GetPath():
            return True
        current = current.GetParent()
    return False


def set_visibility(prim, visible):
    
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


def make_parents_visible(prim):
    """
    Make all parent prims visible up to the root.
    This ensures visibility is not blocked by invisible parents.
    """
    parent = prim.GetParent()
    while parent and parent.GetPath() != "/":
        if UsdGeom.Imageable(parent):
            set_visibility(parent, True)
            print(f"  ↑ Making parent visible: '{parent.GetName()}'")
        parent = parent.GetParent()


def make_children_visible(parent_prim):
    
    #Recursively make all child prims visible.
    
    for child in parent_prim.GetAllChildren():
        if UsdGeom.Imageable(child):
            set_visibility(child, True)
            make_children_visible(child)


def hide_all_scopes_except(target_scope_name, keep_scopes=None):
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
        keep_scopes = ["Models", "Setup", "Lights", "Cameras"]
    
    stage = omni.usd.get_context().get_stage()
    
    if not stage:
        print("Error: No active stage")
        return
    
    # Find the target scope
    target_scope_prim = find_scope_by_name(stage, target_scope_name)
    
    if not target_scope_prim:
        print(f"⚠ ERROR: Scope '{target_scope_name}' not found!")
        return
    
    print(f"\n✓ Found target scope: '{target_scope_name}'")
    print(f"  Path: {target_scope_prim.GetPath()}")
    
    # Find all scopes to keep visible
    keep_scope_prims = {}
    for scope_name in keep_scopes:
        scope_prim = find_scope_by_name(stage, scope_name)
        if scope_prim:
            keep_scope_prims[scope_name] = scope_prim
            print(f"✓ Scope to keep: '{scope_name}' - {scope_prim.GetPath()}")
        else:
            print(f"⚠ Scope '{scope_name}' not found (will be ignored)")
    
    print("\n" + "="*60)
    print("VISIBILITY MODIFICATION:")
    print("="*60)
    
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
                print(f"\n✓ TARGET: '{prim_name}' → VISIBLE")
                set_visibility(prim, True)
                make_children_visible(prim)
                visible_count += 1
                visible_scopes.append(prim_name)
                
            # Child/descendant of target scope: visible
            elif is_descendant_of(prim, target_scope_prim):
                print(f"✓ CHILD OF TARGET: '{prim_name}' → VISIBLE")
                set_visibility(prim, True)
                make_children_visible(prim)
                visible_count += 1
                visible_scopes.append(prim_name)
                
            # Scopes in the exceptions list: visible (but NOT their children)
            elif prim_name in keep_scope_prims and prim_path == keep_scope_prims[prim_name].GetPath():
                print(f"✓ EXCEPTION: '{prim_name}' → VISIBLE")
                set_visibility(prim, True)
                # NOTE: We make children visible here too, but they will be handled individually
                make_children_visible(prim)
                visible_count += 1
                visible_scopes.append(prim_name)
                
            # Other scopes: hide
            else:
                print(f"○ '{prim_name}' → HIDDEN")
                set_visibility(prim, False)
                hidden_count += 1
                hidden_scopes.append(prim_name)
    
    # Make all parents of target scope visible
    print("\n" + "="*60)
    print("MAKING PARENT CHAIN VISIBLE:")
    print("="*60)
    make_parents_visible(target_scope_prim)
    
    # Also make parents of exception scopes visible
    for scope_name, scope_prim in keep_scope_prims.items():
        print(f"\nMaking parent chain visible for '{scope_name}':")
        make_parents_visible(scope_prim)
    
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


# ============================================
# USAGE
# ============================================

hide_all_scopes_except("CD40153U_29Y", keep_scopes=["Models", "Setup", "Lights", "Cameras"])
