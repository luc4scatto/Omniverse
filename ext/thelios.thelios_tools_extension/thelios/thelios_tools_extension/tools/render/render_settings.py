import carb.settings

settings = carb.settings.get_settings()

#Path Tracing settings
settings.set("/rtx/rendermode", "PathTracing")

settings.set("/rtx/pathtracing/maxBounces", 8)
settings.set("/rtx/pathtracing/maxSpecularAndTransmissionBounces", 12)
settings.set("/rtx/pathtracing/maxVolumeBounces", 20)
settings.set("/rtx/pathtracing/ptfog/maxBounces", 2)

#Background settings
settings.set("/rtx/background/source/type",2)
settings.set("/rtx/background/source/color", [1.0, 1.0, 1.0])

settings.set("/rtx/background/source/texture/luminanceScale", 15)

#Post Processing settings
settings.set("/rtx/post/tonemap/ocio/enabled", True)

print("Impostazioni di render aggiornate con successo!")
