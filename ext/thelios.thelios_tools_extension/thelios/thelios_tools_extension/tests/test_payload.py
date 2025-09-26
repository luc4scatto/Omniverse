from pxr import Usd, Sdf, UsdGeom
import omni.kit.commands
import omni.usd
from typing import Optional, List

def assign_payload_with_nested_import(
    stage: Usd.Stage,
    target_scope_path: str,
    payload_asset_path: str,
    payload_target_path: Optional[str] = None,
    load_all_nested: bool = True
) -> Usd.Prim:
    """
    Assegna un payload a uno scope e importa ricorsivamente tutti i payload annidati.
    
    Args:
        stage: Lo stage USD corrente
        target_scope_path: Il percorso dello scope di destinazione
        payload_asset_path: Il percorso del file USD del payload
        payload_target_path: Il percorso del prim target nel payload (opzionale)
        load_all_nested: Se True, carica tutti i payload annidati
    
    Returns:
        Il prim scope con il payload assegnato
    """
    
    # Crea lo scope se non esiste
    scope_path = Sdf.Path(target_scope_path)
    scope_prim = stage.GetPrimAtPath(scope_path)
    
    if not scope_prim.IsValid():
        # Crea uno scope
        scope_prim = UsdGeom.Scope.Define(stage, scope_path).GetPrim()
        print(f"Creato nuovo scope: {target_scope_path}")
    
    # Determina il percorso target del payload
    target_path = Sdf.Path(payload_target_path) if payload_target_path else Sdf.Path.emptyPath
    
    # Aggiungi il payload usando i comandi di Kit
    try:
        omni.kit.commands.execute("AddPayload",
            stage=stage,
            prim_path=scope_path,
            payload=Sdf.Payload(
                assetPath=payload_asset_path,
                primPath=target_path
            )
        )
        print(f"Payload aggiunto con successo a {target_scope_path}")
    except Exception as e:
        print(f"Errore nell'aggiunta del payload: {e}")
        return scope_prim
    
    # Se richiesto, carica tutti i payload annidati
    if load_all_nested:
        _load_all_nested_payloads(stage, scope_prim)
    
    return scope_prim

def _load_all_nested_payloads(stage: Usd.Stage, root_prim: Usd.Prim) -> None:
    """
    Funzione helper per caricare ricorsivamente tutti i payload annidati.
    
    Args:
        stage: Lo stage USD
        root_prim: Il prim radice da cui iniziare la ricerca ricorsiva
    """
    
    # Configura le regole di caricamento per caricare tutti i payload
    load_rules = Usd.StageLoadRules.LoadAll()
    stage.SetLoadRules(load_rules)
    
    # Attraversa ricorsivamente tutti i discendenti
    for prim in root_prim.GetDescendants():
        if prim.HasPayload():
            # Carica esplicitamente ogni payload trovato
            payloads = prim.GetPayloads()
            payload_list = payloads.GetAddedOrExplicitItems()
            
            for payload in payload_list:
                print(f"Caricamento payload annidato: {payload.assetPath} su {prim.GetPath()}")
                
                # Assicurati che il payload sia caricato
                if not prim.IsLoaded():
                    prim.Load()
                    
def assign_payload_advanced(
    target_scope_path: str,
    payload_asset_path: str
) -> Usd.Prim:
    """
    Versione avanzata che utilizza il contesto Omniverse corrente.
    
    Args:
        target_scope_path: Il percorso dello scope di destinazione
        payload_asset_path: Il percorso del file USD del payload
        payload_target_path: Il percorso del prim target nel payload (opzionale)
        context_name: Nome del contesto USD (opzionale, usa quello corrente se None)
    
    Returns:
        Il prim scope con il payload assegnato
    """
    
    # Ottieni il contesto USD corrente
    context = omni.usd.get_context()
    stage = context.get_stage()
    
    if not stage:
        raise RuntimeError("Nessuno stage attivo trovato")
    
    return assign_payload_with_nested_import(
        stage, 
        target_scope_path, 
        payload_asset_path, 
        
    )

def get_nested_payloads_info(stage: Usd.Stage, prim_path: str) -> List[dict]:
    """
    Ottieni informazioni su tutti i payload annidati in un prim.
    
    Args:
        stage: Lo stage USD
        prim_path: Il percorso del prim da analizzare
    
    Returns:
        Lista di dizionari con informazioni sui payload
    """
    
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        return []
    
    payloads_info = []
    
    # Analizza ricorsivamente tutti i discendenti
    for descendant in prim.GetDescendants():
        if descendant.HasPayload():
            payloads = descendant.GetPayloads()
            payload_list = payloads.GetAddedOrExplicitItems()
            
            for payload in payload_list:
                payload_info = {
                    'prim_path': str(descendant.GetPath()),
                    'asset_path': payload.assetPath,
                    'prim_target': str(payload.primPath) if payload.primPath else 'default',
                    'is_loaded': descendant.IsLoaded()
                }
                payloads_info.append(payload_info)
    
    return payloads_info

# Esempio di utilizzo
def esempio_utilizzo():
    """Esempio di come utilizzare le funzioni."""
    
    payload_usd = r"H:\Prototyping_PD\Rendering\USDProject\USD\DIOR\CD40235I\sku\CD40235I_52E.usd"
    prim_path = "/World/Models/glass_Xform/CD40235I_Xform/Release_261/CD40235I_52E"
    # Utilizzando il contesto Omniverse corrente
    try:
        scope_prim = assign_payload_advanced(
            target_scope_path=prim_path,
            payload_asset_path=payload_usd,
        )
        
        print(f"Payload assegnato con successo al scope: {scope_prim.GetPath()}")
        
        # Ottieni informazioni sui payload annidati
        context = omni.usd.get_context()
        stage = context.get_stage()
        
        #nested_info = get_nested_payloads_info(stage, prim_path)
        #print(f"Trovati {len(nested_info)} payload annidati:")
        
        #for info in nested_info:
        #    print(f"  - {info['prim_path']}: {info['asset_path']} (caricato: {info['is_loaded']})")
            
    except Exception as e:
        print(f"Errore: {e}")

esempio_utilizzo()