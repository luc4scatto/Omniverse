import omni.ext
from omni.kit.viewport.utility import get_active_viewport_window

#Custom modules
from .window import TheliosToolsWindow
from .models import TheliosWindowModel
from .tools.style import style_widgets
from .logic import TheliosLogic

DARK_WINDOW_STYLE = style_widgets.window_style()
CollapsableFrame_style = style_widgets.collapbsable_style()

class TheliosExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        print("[thelios_tools_extension] Thelios Tools Extension initialized")
        
    def on_startup(self, ext_id):
        
        thelios_models = TheliosWindowModel()
        viewport_window = get_active_viewport_window()
        logic = TheliosLogic(thelios_models)
        if viewport_window is not None:
            self.thelios_tools = TheliosToolsWindow(thelios_models, viewport_window, logic, ext_id)
            
    def on_shutdown(self):
        # Clean-up degli handlers e UI
        self.window = None