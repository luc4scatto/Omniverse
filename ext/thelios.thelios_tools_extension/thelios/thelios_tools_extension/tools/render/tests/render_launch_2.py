import asyncio
import carb
import carb.settings

from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window,capture_viewport_to_file
import omni.kit.actions.core
import omni.usd
import omni.timeline

#from .viewport_capture import render_png

def render_png(output_path: str):
    
    #Disable selection to avoid UI elements in the capture
    selection = omni.usd.get_context().get_selection()
    selection.clear_selected_prim_paths()
    
    async def capture(filePath : str, hdr : bool = False):
        
        # Assign ldr/hdr in settings.
        settings = carb.settings.get_settings()
        prevAsyncRendering = settings.get("/app/asyncRendering")
        prevAsyncRenderingLowLatency = settings.get("/app/asyncRenderingLowLatency")
        prevHdr = settings.get("/app/captureFrame/hdr")
        
        settings.set("/app/asyncRendering", False)
        settings.set("/app/asyncRenderingLowLatency", False)
        settings.set("/app/captureFrame/hdr", hdr)
        
        # Get active viewport.
        active_viewport = get_active_viewport()
        
        await active_viewport.wait_for_rendered_frames()
        
        # Capturing.
        cap_obj = capture_viewport_to_file(active_viewport, filePath)
        await omni.kit.app.get_app_interface().next_update_async()
        
        # awaiting completion.
        result = await cap_obj.wait_for_result(completion_frames=30)
        
        settings.set("/app/asyncRendering", prevAsyncRendering)
        settings.set("/app/asyncRenderingLowLatency", prevAsyncRenderingLowLatency)
        settings.set("/app/captureFrame/hdr", prevHdr)
        
        print(f"Capture complete [{filePath}].")
        
    # -------------------------------------------.
    asyncio.ensure_future( capture(output_path) )
    
def viewport_settings(res: str):
    resolution_parts = res.split("x")
    width = int(resolution_parts[0])
    height = int(resolution_parts[1])
    final_res = (width, height)
    
    viewport_window = get_active_viewport_window()
    viewport_api = viewport_window.viewport_api
    
    viewport_api.fill_frame = False  # disattiva l'adattamento automatico
    viewport_api.resolution = final_res

def get_filename(frame: str, ext: str = "png") -> str:
    
    sku_name = "CD40153U_32P"
    file_name = f"{sku_name}_{frame}.{ext}"
    return file_name
    
def render_launch_png(resolution: str, 
                    output_path: str,
                    bool_value: bool,
                    start_frame: int,
                    end_frame: int,
                    single_frame: int):
    
    viewport_settings(resolution)
    timeline = omni.timeline.get_timeline_interface()
    
    async def render_png(output_path: str):
        if bool_value:
            for frame in range(start_frame, end_frame + 1):
                print(f"current_frame: {frame}")
                custom_output = f"{output_path}{get_filename(str(frame),"png")}"
                timeline.set_current_time(frame)
                
                active_viewport = get_active_viewport()
                await active_viewport.wait_for_rendered_frames()
                #timeline.update_timeline()
                render_png(custom_output)
        else:
            custom_output = f"{output_path}{get_filename(str(frame),"png")}"
            timeline.set_current_time(single_frame)
            #timeline.update_timeline()
            render_png(custom_output)
        
        print(f"output_path: {custom_output}, bool_value: {bool_value}, start_frame: {start_frame}, end_frame: {end_frame}, single_frame: {single_frame}")
    asyncio.ensure_future( render_png(output_path) )