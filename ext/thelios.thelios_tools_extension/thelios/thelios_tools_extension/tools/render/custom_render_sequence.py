import asyncio
import os
import carb
import carb.settings
import omni.usd
import omni.timeline
from omni.kit.viewport.utility import get_active_viewport, get_active_viewport_window, capture_viewport_to_file
import omni.kit.capture.viewport as viewport_capture

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
        prevAlpha = settings.get("/app/captureFrame/saveAlpha")  # potenziale chiave per alpha
        
        settings.set("/app/asyncRendering", False)
        settings.set("/app/asyncRenderingLowLatency", False)
        settings.set("/app/captureFrame/hdr", hdr)
        settings.set("/app/captureFrame/saveAlpha", True)   # abilita alpha
        
        for _ in range(wait_frames):
            await omni.kit.app.get_app_interface().next_update_async()
        await self.viewport.wait_for_rendered_frames()
        
        cap_obj = capture_viewport_to_file(
            self.viewport,
            file_path
        )
        
        await cap_obj.wait_for_result(completion_frames=30)
        
        # Ripristina impostazioni
        settings.set("/app/asyncRendering", prevAsyncRendering)
        settings.set("/app/asyncRenderingLowLatency", prevAsyncRenderingLowLatency)
        settings.set("/app/captureFrame/hdr", prevHdr)
        settings.set("/app/captureFrame/saveAlpha", prevAlpha)
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
        
        
    def start_capture_extension_render(self):
        
        self.viewport_settings(self.resolution)
        width, height = map(int, self.resolution.split("x"))
        
        #fps = self.get_fps_from_settings()
        #self.set_timeline_frame(frame, fps)
        
        capture_extension = omni.kit.capture.viewport.CaptureExtension.get_instance()
        
        if self.sequence == True:
            start_frame = self.start_frame
            end_frame = self.end_frame
        else:
            start_frame = self.single_frame
            end_frame = self.single_frame
            
        print(f"Start frame: {start_frame}")
        print(f"End frame: {end_frame}")
        
        capture_extension.options._output_folder = self.output_path
        capture_extension.options._file_type = constants.EXT
        capture_extension.options._save_alpha = constants.SAVE_ALPHA
        capture_extension.options._res_width = width
        capture_extension.options._res_height = height
        capture_extension.options._path_trace_spp = constants.PATH_TRACE_SPP
        capture_extension.options._preroll_frames = constants.PREROLL_FRAMES
        capture_extension.options._start_frame = start_frame
        capture_extension.options._end_frame = end_frame
        capture_extension.options._overwrite_existing_frames = True
        capture_extension.options._file_name = self.sku_name
        capture_extension.options._file_name_num_pattern = ".##"
        capture_extension.options._render_product = True
        capture_extension.start()
        
    async def wait_for_render_completion(self, start_frame, end_frame, ext=constants.EXT, timeout=600):
        expected_files = [f"{self.sku_name}.0{frame}.{ext}" for frame in range(start_frame, end_frame+1)]
        elapsed = 0
        poll_interval = 1
        
        self.output_path = os.path.join(self.output_path, f"{self.sku_name}_frames")
        
        while elapsed < timeout:
            try:
                files = os.listdir(self.output_path)
                print(f"Polling in directory: {self.output_path}")
            except Exception as e:
                print(f"Errore accesso directory output: {e}")
                return False
            
            missing = [f for f in expected_files if f not in files]
            print(f"Attesa render: files mancanti {missing} - tempo trascorso {elapsed}s")
            
            if not missing:
                print("Render sequence completata.")
                return True
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        print("Timeout su attesa render sequence.")
        return False
    
    
    async def start_capture_extension_render_async(self):
        
        self.viewport_settings(self.resolution)
        width, height = map(int, self.resolution.split("x"))
        
        #fps = self.get_fps_from_settings()
        #self.set_timeline_frame(frame, fps)
        
        capture_extension = omni.kit.capture.viewport.CaptureExtension.get_instance()
        
        if self.sequence == True:
            start_frame = self.start_frame
            end_frame = self.end_frame
        else:
            start_frame = self.single_frame
            end_frame = self.single_frame
            
        print(f"Start frame: {start_frame}")
        print(f"End frame: {end_frame}")
        print(f"Output path for render: {self.output_path}")
        
        capture_extension.options._output_folder = self.output_path
        capture_extension.options._file_type = constants.EXT
        capture_extension.options._save_alpha = constants.SAVE_ALPHA
        capture_extension.options._res_width = width
        capture_extension.options._res_height = height
        capture_extension.options._path_trace_spp = constants.PATH_TRACE_SPP
        capture_extension.options._preroll_frames = constants.PREROLL_FRAMES
        capture_extension.options._start_frame = start_frame
        capture_extension.options._end_frame = end_frame
        capture_extension.options._overwrite_existing_frames = True
        capture_extension.options._file_name = self.sku_name
        capture_extension.options._file_name_num_pattern = ".##"
        #capture_extension.options._hdr_output = True
        #capture_extension.options._render_product = True
        capture_extension.start()
        
        print(f"CaptureExtension started for {self.sku_name} from frame {start_frame} to {end_frame} at resolution {self.resolution}")
        
        await self.wait_for_render_completion(start_frame, end_frame)
        

# from my_script import OmniCustomSequenceRenderer
# renderer = OmniCustomSequenceRenderer(sku_name="CD40153U_32P")
# asyncio.ensure_future(
#     renderer.render_sequence("2048x2048", "C:/Users/l.scattolin/Desktop/Renders/", True, 1, 2, 1, wait_frames=60)
# )
#choose camera to render
"""
from omni.kit.viewport.utility import get_active_viewport

camera_path = "/World/Camera/MyNewCamera"
viewport = get_active_viewport()

if not viewport:
    raise RuntimeError("No active Viewport")

# Set the Viewport's active camera to the
# camera prim path you want to switch to.
viewport.camera_path = camera_path
"""