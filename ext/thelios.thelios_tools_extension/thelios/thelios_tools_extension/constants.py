from pathlib import Path
import omni.ui as ui
from omni.ui import color as cl

DB_KEY = "Driver={SQL Server}; Server=10.189.24.40; uid=rendering_dep; pwd=251_ee5FJK?58fde723c8cf9c!; Trusted_Connection=No;"

LABEL_PADDING = 70
RESOLUTIONS = ("1920x1920","2048x2048","4096x4096")
DEFAULT_RELEASE = 262

#Sequence const
START_FRAME = 1
END_FRAME = 8
SING_SEQ = True

GENRES = [
            "Optical - Man",
            "Optical - Woman",
            "Sun - Man",
            "Sun - Woman",
            "All Man",
            "All Woman"
        ]

#Paths
BLOB_PATH = r"H:\\Prototyping_PD\\Rendering\\USDProject\\USD\\DIOR"
TEMPLATES_PATH = Path(__file__).parent.joinpath("tools","templates")

#When collapsed is True, the UI module will be hidden by default
IMPORT_TEMPLATE_UI_VISIBILITY = False
IMPORT_ALL_COLLECTION_UI_VISIBILITY = True
CUSTOM_IMPORT_TEMPLATE_UI_VISIBILITY = False
CUSTOM_MODEL_IMPORT_UI_VISIBILITY = True

#Styles
SLIDER_ENABLED_STYLE = {
                        "background_color": 0xFF23211F,
                        "secondary_color": cl(0.6),
                        "color": cl(0.9),
                        "draw_mode": ui.SliderDrawMode.HANDLE
                        }

SLIDER_DISABLED_STYLE = {
                        "background_color": cl(0.5),
                        "secondary_color": cl(0.6),
                        "color": cl(0.7),
                        "draw_mode": ui.SliderDrawMode.HANDLE
                        }