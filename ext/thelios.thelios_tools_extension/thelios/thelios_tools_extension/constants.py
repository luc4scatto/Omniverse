from pathlib import Path
import omni.ui as ui
from omni.ui import color as cl

# DB connection string -----------------------------------------

DB_KEY = "Driver={SQL Server}; Server=10.189.24.40; uid=rendering_dep; pwd=251_ee5FJK?58fde723c8cf9c!; Trusted_Connection=No;"

#Sequence const -------------------------------------------------

DEFAULT_RELEASE = 262
START_FRAME = 1
END_FRAME = 8
SEQUENCE = True
SINGLE_FRAME = False

GENRES = [
            "Optical - Man",
            "Optical - Woman",
            "Sun - Man",
            "Sun - Woman",
            "All Man",
            "All Woman"
        ]

#Paths --------------------------------------------------------

BLOB_PATH = r"H:\\Prototyping_PD\\Rendering\\USDProject\\USD\\DIOR"
TEMPLATES_PATH = Path(__file__).parent.joinpath("tools","templates")

#UI Visibility ------------------------------------------------

#When collapsed is True, the UI module will be hidden by default
IMPORT_TEMPLATE_UI_VISIBILITY = False
IMPORT_ALL_COLLECTION_UI_VISIBILITY = True
CUSTOM_IMPORT_TEMPLATE_UI_VISIBILITY = False
CUSTOM_MODEL_IMPORT_UI_VISIBILITY = True

#Styles ------------------------------------------------------

LABEL_PADDING = 70

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

#Render settings ---------------------------------------------

RESOLUTIONS = ("1920x1920","2048x2048","4096x4096")

SAMPLE_PER_PIXEL = 16
TOTAL_SPP = 1024
ADAPTIVE_SAMPLING_ENABLED = True
TARGET_ERROR = 0.0005

MAX_BOUNCES = 64
MAX_SPEC_TRANSM_BOUNCES = 64
MAX_VOLUME_BOUNCES = 32
MAX_FOG_BOUNCES = 2

BACKGROUND_TYPE = 0
BACKGROUND_COLOR = [1.0, 1.0, 1.0]

LUM_SCALE = 15
OCIO_ENABLED = True

EXT = "png"
WAIT_FRAMES = 300

ANTI_ALIASING_PATTERN = 3


#USD variables ----------------------------------------------

CAMERA_TARGET = "/World/Setup/Cameras"
LIGHT_TARGET = "/World/Setup/Lights"
LIMBO_TARGET = "/World/Setup/Limbo"
WORLD_PATH = "/World"

#-------------------------------------------------------------

TEMP_NAME = "CD40153U_32P"