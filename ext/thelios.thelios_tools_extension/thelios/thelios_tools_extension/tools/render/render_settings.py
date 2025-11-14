import carb.settings
from ... import constants

def import_render_settings():
    
    settings = carb.settings.get_settings()
    
    #Path Tracing settings
    settings.set("/rtx/rendermode", "PathTracing")
    
    settings.set("/rtx/pathtracing/spp", constants.SAMPLE_PER_PIXEL)
    settings.set("/rtx/pathtracing/totalSpp", constants.TOTAL_SPP)
    settings.set("/rtx/pathtracing/adaptiveSampling/enabled", constants.ADAPTIVE_SAMPLING_ENABLED)
    settings.set("/rtx/pathtracing/adaptiveSampling/targetError", constants.TARGET_ERROR)
    
    settings.set("/rtx/pathtracing/maxBounces", constants.MAX_BOUNCES)
    settings.set("/rtx/pathtracing/maxSpecularAndTransmissionBounces", constants.MAX_SPEC_TRANSM_BOUNCES)
    settings.set("/rtx/pathtracing/maxVolumeBounces", constants.MAX_VOLUME_BOUNCES)
    settings.set("/rtx/pathtracing/ptfog/maxBounces", constants.MAX_FOG_BOUNCES)
    
    #Anti-Aliasing settings
    settings.set("/rtx/pathtracing/aa/op", constants.ANTI_ALIASING_PATTERN)
    
    #Background settings
    settings.set("/rtx/background/source/type", constants.BACKGROUND_TYPE)
    settings.set("/rtx/background/source/color", constants.BACKGROUND_COLOR)
    
    settings.set("/rtx/background/source/texture/luminanceScale", constants.LUM_SCALE)
    
    #Post Processing settings
    settings.set("/rtx/post/tonemap/ocio/enabled", constants.OCIO_ENABLED)
    
    print("Impostazioni di render aggiornate con successo!")
