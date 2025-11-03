import asyncio
import carb
import carb.settings
import omni.usd
import omni.timeline
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window, capture_viewport_to_file

from ... import constants

class OmniCustomSequenceRenderer:
    def __init__(self, sku_name: str, 
                        resolution: str, 
                        output_path: str,
                        sequence: bool,
                        start_frame: int,
                        end_frame: int,
                        single_frame: int):
        
        self.end_frame = end_frame
        self.single_frame = single_frame
        self.start_frame = start_frame
        self.sequence = sequence
        self.resolution = resolution
        self.output_path = output_path
        self.sku_name = sku_name
        
        self.timeline = omni.timeline.get_timeline_interface()
        self.viewport = get_active_viewport()
        self.viewport_window = get_active_viewport_window()
    
    def get_filename(self, frame: int, ext: str = constants.EXT) -> str:
        return f"{self.sku_name}_{frame}.{ext}"
    
    def viewport_settings(self, res: str):
        width, height = map(int, res.split("x"))
        self.viewport_window.viewport_api.fill_frame = False
        self.viewport_window.viewport_api.resolution = (width, height)
        
        # Clear selection to avoid UI elements
        selection = omni.usd.get_context().get_selection()
        selection.clear_selected_prim_paths()
        
    def get_fps_from_settings(self):
        settings = carb.settings.get_settings()
        fps = settings.get("/persistent/app/timeline/fps")
        if not fps:
            fps = settings.get("/app/timeline/fps")
        if not fps:
            fps = 60
        return fps
    
    def set_timeline_frame(self, frame_num: int, fps: int):
        self.timeline.set_current_time(frame_num / fps)
        
    def get_timeline_frame(self, fps: int):
        return int(round(self.timeline.get_current_time() * fps))
    
    async def capture_and_save_png(self, file_path: str, hdr=False, wait_frames: int=60):
        settings = carb.settings.get_settings()
        prevAsyncRendering = settings.get("/app/asyncRendering")
        prevAsyncRenderingLowLatency = settings.get("/app/asyncRenderingLowLatency")
        prevHdr = settings.get("/app/captureFrame/hdr")
        settings.set("/app/asyncRendering", False)
        settings.set("/app/asyncRenderingLowLatency", False)
        settings.set("/app/captureFrame/hdr", hdr)
        for _ in range(wait_frames):
            await omni.kit.app.get_app_interface().next_update_async()
        await self.viewport.wait_for_rendered_frames()
        cap_obj = capture_viewport_to_file(self.viewport, file_path)
        await cap_obj.wait_for_result(completion_frames=30)
        settings.set("/app/asyncRendering", prevAsyncRendering)
        settings.set("/app/asyncRenderingLowLatency", prevAsyncRenderingLowLatency)
        settings.set("/app/captureFrame/hdr", prevHdr)
        print(f"Capture complete [{file_path}].")
    
    async def render_sequence(self, wait_frames: int=constants.WAIT_FRAMES):
        
        self.viewport_settings(self.resolution)
        self.timeline.set_auto_update(False)
        self.timeline.pause()
        fps = self.get_fps_from_settings()
        
        if self.sequence:
            for frame in range(self.start_frame, self.end_frame + 1):
                print(f"Rendering frame: {frame}")
                self.set_timeline_frame(frame, fps)
                await asyncio.sleep(0.3)
                for _ in range(5):
                    await omni.kit.app.get_app_interface().next_update_async()
                #print(f"Current timeline time (seconds): {self.timeline.get_current_time()}")
                #print(f"Current timeline frame: {self.get_timeline_frame(fps)}")
                filename = f"{self.output_path}{self.get_filename(frame, 'png')}"
                await self.capture_and_save_png(filename, wait_frames=wait_frames)
        else:
            frame = self.single_frame
            self.set_timeline_frame(frame, fps)
            await asyncio.sleep(0.3)
            for _ in range(5):
                await omni.kit.app.get_app_interface().next_update_async()
            #print(f"Current timeline time (seconds): {self.timeline.get_current_time()}")
            #print(f"Current timeline frame: {self.get_timeline_frame(fps)}")
            filename = f"{self.output_path}{self.get_filename(frame, 'png')}"
            await self.capture_and_save_png(filename, wait_frames=wait_frames)
            
        self.timeline.set_auto_update(True)
        print(f"Render sequence complete. Output path: {self.output_path}")

# from my_script import OmniCustomSequenceRenderer
# renderer = OmniCustomSequenceRenderer(sku_name="CD40153U_32P")
# asyncio.ensure_future(
#     renderer.render_sequence("2048x2048", "C:/Users/l.scattolin/Desktop/Renders/", True, 1, 2, 1, wait_frames=60)
# )
