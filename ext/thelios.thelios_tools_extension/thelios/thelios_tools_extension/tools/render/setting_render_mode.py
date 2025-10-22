import omni.kit
import carb.settings
import asyncio

# Get Render Mode.
settings = carb.settings.get_settings()
renderMode = settings.get('/rtx/rendermode')

# rtx, iray
activeRender = settings.get('/renderer/active')

if activeRender == 'iray':
    print("Render Mode : Iray")
else:
    if renderMode == 'RaytracedLighting':
        print("Render Mode : RTX Real-time")
    else:
        if renderMode == 'PathTracing':
            print("Render Mode : RTX Path-traced")
        else:
            print("Render Mode : " + renderMode)

# Set Render mode.
# It is safe to wait for one frame in the coroutine to change the RenderMode.
async def SetRenderMode (modeName : str):
    await omni.kit.app.get_app().next_update_async()
    settings.set('/rtx/rendermode', modeName)

# Set "RTX Real-time"
asyncio.ensure_future(SetRenderMode('RaytracedLighting'))

# Set "RTX Path-traced"
asyncio.ensure_future(SetRenderMode('PathTracing'))


# Get rendering size.
# If Render Resolution is "Viewport", -1 will be set.
settings = carb.settings.get_settings()
width  = settings.get('/app/renderer/resolution/width')
height = settings.get('/app/renderer/resolution/height')

print("Rendering size : " + str(width) + " x " + str(height))

# Set rendering size.
#settings.set('/app/renderer/resolution/width', 1280)
#settings.set('/app/renderer/resolution/height', 720)