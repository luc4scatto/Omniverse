from pxr import Usd, Sdf, UsdGeom
import omni.kit.commands
import omni.usd


def assign_payload(target_path: str, payload_asset_path: str) -> Usd.Prim:
    """
    Assegna un payload al prim preservando i figli esistenti.
    Non gestisce payload annidati - li lascia caricare normalmente.
    """
    
    context = omni.usd.get_context()
    stage = context.get_stage()
    
    if not stage:
        raise RuntimeError("Nessuno stage attivo trovato")
    
    # Trova o crea il prim target
    target_prim = _get_or_create_prim(stage, target_path)
    
    # Aggiungi il payload direttamente al prim
    omni.kit.commands.execute("AddPayload",
        stage=stage,
        prim_path=target_prim.GetPath(),
        payload=Sdf.Payload(assetPath=payload_asset_path)
    )
    
    print(f"Payload aggiunto a: {target_prim.GetPath()}")
    
    # Carica tutti i payload normalmente (senza gestione speciale dei nested)
    stage.SetLoadRules(Usd.StageLoadRules.LoadAll())
    
    return target_prim

def _get_or_create_prim(stage: Usd.Stage, path: str) -> Usd.Prim:
    """Trova prim esistente o crea gerarchia se necessario."""
    
    # Prima cerca per nome
    prim_name = path.split("/")[-1]
    for prim in stage.Traverse():
        if prim.GetName() == prim_name:
            return prim
    
    # Se non trovato, crea la gerarchia
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
    Importa un payload senza gestire payload annidati.
    """
    try:
        assign_payload(
            target_path=target_path,
            payload_asset_path=payload_usd_path
        )
        print("Import completato")
        
    except Exception as e:
        print(f"Errore: {e}")
        


target_path = "/World/Models/glass_Xform/CD40235I_Xform/Release_261/CD40235I_52E"
# Utilizzo
payload_usd = r"H:\Prototyping_PD\Rendering\USDProject\USD\DIOR\CD40235I\sku\CD40235I_52E.usd"
import_payload(payload_usd, target_path)

#//10.189.88.1/Company/Prototyping_PD/Rendering/USDProject/USD/DIOR/CD40235I/sku/CD40235I_52E.usd
#/World/Models/glass_Xform/CD40235I_Xform/Release_261/CD40235I_52E