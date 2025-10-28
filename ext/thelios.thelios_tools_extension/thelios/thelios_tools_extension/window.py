import omni.ui as ui
import omni.usd
from omni.ui import scene
import carb

#from .utils import load_config
from .ui import style_widgets
from .ui_modules_import import ImportTemplateUI, CustomModelImportPanel
from .models import TheliosWindowModel
from .logic import TheliosLogic

DARK_WINDOW_STYLE = style_widgets.window_style()
CollapsableFrame_style = style_widgets.collapbsable_style()


class TheliosToolsWindow:

    WINDOW_NAME = "Movie Capture"

    def __init__(self, model:TheliosWindowModel, vp_win: ui.Window, logic: TheliosLogic, ext_id: str ):
        
        self.model = model
        self.logic = logic
        self.vp_win = vp_win
        self.ext_id = ext_id
        
        self._init()
        
        
        
        # Create main window
        
        
        """
        self._stage = omni.usd.get_context().get_stage()
        self.brand_combo = None
        self.type_combo = None
        self.release_field = None
        self.resolution_combo = None
        
        """
        #self._timeline = omni.timeline.get_timeline_interface()
        #self._current_fps = self._timeline.get_time_codes_per_seconds()

    def _init(self):
        
        self._editor_window = None
        """
        self._window_Frame = None
        self._window_Frame.set_style(DARK_WINDOW_STYLE)
        """
        self.width = 450
        self.height = 600
        
        self._editor_window = ui.Window("Thelios USD Tools", width=self.width, height=self.height)
        self._editor_window.deferred_dock_in("Layers")
        self._editor_window.setPosition(450, 100)
        self._editor_window.frame.set_style(DARK_WINDOW_STYLE)
        
        with self._editor_window.frame:
            with ui.VStack():
                self._window_Frame = ui.ScrollingFrame(
                    name="canvas",
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                )
                with self._window_Frame:
                    with ui.VStack(height=0, name="main_v_stack", spacing=8):
                        
                        #Import template panel
                        self.import_template_panel = ImportTemplateUI()
                        self.import_template_panel.build(CollapsableFrame_style)
                        
                        self.custom_model_import_panel = CustomModelImportPanel(self.model, self.logic)
                        self.custom_model_import_panel.build(CollapsableFrame_style)
                        
                        
                        
        return self._editor_window