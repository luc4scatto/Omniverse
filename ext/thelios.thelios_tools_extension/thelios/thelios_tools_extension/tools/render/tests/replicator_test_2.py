import omni.replicator.core as rep  # Replicator API [web:8]
import carb
import asyncio
from pxr import Usd, Sdf
import omni.usd
import omni.timeline

release_scope="/World/Models/glass_Xform/CD40235I_Xform/Release_261"
output_path = "C:/renders/Release_261"

def get_stage():
    return omni.usd.get_context().get_stage()  # Usd.Stage [web:3]

def get_prim(path: str) -> Usd.Prim:
    return get_stage().GetPrimAtPath(Sdf.Path(path))  # [web:3]

def set_payload_enabled(prim: Usd.Prim, enabled: bool):
    # Forza il carico/sCarico del payload su quel prim
    if enabled:
        prim.Load()      # carica il payload composito [web:3]
    else:
        prim.Unload()    # scarica il payload composito [web:3]

# Risolve una camera: usa quella selezionata o la prima trovata
def get_active_camera_path():
    stage = get_stage()
    it = stage.Traverse()
    for p in it:
        if p.GetTypeName() == "Camera":
            return str(p.GetPath())
    raise RuntimeError("Nessuna camera trovata")  # [web:3]

async def render_n_frames(rp, n_frames: int, out_pattern: str):
    writer = rep.WriterRegistry.get("BasicWriter")  # writer semplice [web:8]
    writer.initialize(output_dir=out_pattern, rgb=True)  # salva LDR rgb [web:8]
    writer.attach([rp])  # collega il render product [web:8]
    for _ in range(n_frames):
        await omni.usd.get_context().next_usd_async()  # attende il frame [web:3]
    writer.detach()  # libera VRAM [web:8]
    
async def render_queue_release_261(base_scope=release_scope,
                                    payload_names=("CD40235I_52E", "CD40235I_69A"),
                                    frames_each=8,
                                    res=(1920,1080),
                                    out_root=output_path):
    # Disattiva tutto
    payload_prims = [get_prim(f"{base_scope}/{name}") for name in payload_names]  # [web:3]
    for p in payload_prims:
        if p and p.IsValid():
            set_payload_enabled(p, False)  # scarica all’inizio [web:3]

    # RenderProduct una volta sola dalla camera
    cam_path = get_active_camera_path()  # [web:3]
    rp = rep.create.render_product(cam_path, resolution=res, force_new=True, name="QueueRP")  # [web:8]

    # Esegui la "queue": uno alla volta
    for name, prim in zip(payload_names, payload_prims):
        if not prim or not prim.IsValid():
            carb.log_warn(f"Payload {name} non trovato, salto")  # [web:3]
            continue
        # abilita solo quello corrente
        for other in payload_prims:
            if other != prim and other and other.IsValid():
                set_payload_enabled(other, False)  # [web:3]
        set_payload_enabled(prim, True)  # abilita il corrente [web:3]

        # attendi che USD completi il caricamento prima di renderizzare
        await omni.usd.get_context().next_stage_event_async()  # sincronizza composizione [web:3]

        # cartella di output distinta per payload
        out_dir = f"{out_root}/{name}"
        await render_n_frames(rp, frames_each, out_dir)  # 8 frame [web:8][web:3]

    # pulizia finale
    rep.destroy.render_product(rp)  # libera il RP [web:8]
