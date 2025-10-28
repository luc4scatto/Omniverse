import carb.settings
from omni.kit.viewport.utility import get_active_viewport_window

def import_render_settings():
    
    settings = carb.settings.get_settings()

    #Path Tracing settings
    settings.set("/rtx/rendermode", "PathTracing")

    settings.set("/rtx/pathtracing/spp", 16)
    settings.set("/rtx/pathtracing/totalSpp", 1024)
    settings.set("/rtx/pathtracing/adaptiveSampling/enabled", True)
    
    settings.set("/rtx/pathtracing/maxBounces", 32)
    settings.set("/rtx/pathtracing/maxSpecularAndTransmissionBounces", 32)
    settings.set("/rtx/pathtracing/maxVolumeBounces", 16)
    settings.set("/rtx/pathtracing/ptfog/maxBounces", 2)

    #Background settings
    settings.set("/rtx/background/source/type",2)
    settings.set("/rtx/background/source/color", [1.0, 1.0, 1.0])

    settings.set("/rtx/background/source/texture/luminanceScale", 15)

    #Post Processing settings
    settings.set("/rtx/post/tonemap/ocio/enabled", True)

    print("Impostazioni di render aggiornate con successo!")
