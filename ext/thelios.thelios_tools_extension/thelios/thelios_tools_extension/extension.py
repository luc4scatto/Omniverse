import omni.ext
import omni.ui as ui
import omni.usd

from omni.kit.viewport.utility import get_active_viewport_window

#Custom modules

from .window import TheliosToolsWindow
from .models import TheliosWindowModel
from .tools.style import style_widgets
from .logic import TheliosLogic

DARK_WINDOW_STYLE = style_widgets.window_style()
CollapsableFrame_style = style_widgets.collapbsable_style()

"""
from .models import RenderSettings, SKU
from .ui_components import RenderPanel
from .logic import get_plm_data, batch_import_payload
from .constants import LABEL_PADDING, RESOLUTIONS
"""


class TheliosExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        print("[thelios_tools_extension] Thelios Tools Extension initialized")
        """
        # Modello dati - configurazioni render
        self.render_settings = RenderSettings("", RESOLUTIONS[0], 1, 8, 1)
        # Istanzia pannelli UI modulari passandogli i modelli dati
        self.render_panel = RenderPanel(self.render_settings)
        self.window = None
        self.stage = None
        """
    def on_startup(self, ext_id):
        
        thelios_models = TheliosWindowModel()
        viewport_window = get_active_viewport_window()
        logic = TheliosLogic(thelios_models)
        if viewport_window is not None:
            self.thelios_tools = TheliosToolsWindow(thelios_models, viewport_window, logic, ext_id)

    """
    def on_render_click(self):
        # Recupera i dati dal modello e chiama la logica business
        batch_import_payload(self.stage, self.render_panel.get_selected_skus())
    """
    def on_shutdown(self):
        # Clean-up degli handlers e UI
        self.window = None