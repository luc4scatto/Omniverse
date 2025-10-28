import omni.ui as ui
import omni.usd
from omni.ui import scene
import carb

#from .utils import load_config
from .tools.style import style_widgets
from .ui_modules_import import ImportTemplatePanel, CustomModelImportPanel, CustomTemplateImportPanel, ImportAllCollectionPanel, RenderSettingsPanel
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
        
        #self._timeline = omni.timeline.get_timeline_interface()
        #self._current_fps = self._timeline.get_time_codes_per_seconds()
        
    def _init(self):
        
        self._editor_window = None
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
                        
                        #Import template panel class
                        self.import_template_panel = ImportTemplatePanel()
                        self.import_template_panel.build(CollapsableFrame_style)
                        
                        #Import custom template panel class
                        self.custom_template_import_panel = CustomTemplateImportPanel(self.model, self.logic)
                        self.custom_template_import_panel.build(CollapsableFrame_style)
                        
                        #Import custom model panel class
                        self.custom_model_import_panel = CustomModelImportPanel(self.model, self.logic)
                        self.custom_model_import_panel.build(CollapsableFrame_style)
                        
                        #Import all collection panel class
                        self.import_all_collection_panel = ImportAllCollectionPanel(self.model, self.logic)
                        self.import_all_collection_panel.build(CollapsableFrame_style)
                        
                        #Import render settings panel class
                        self.render_panel = RenderSettingsPanel(self.model, self.logic)
                        self.render_panel.build(CollapsableFrame_style)
                        
        return self._editor_window