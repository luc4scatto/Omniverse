from pathlib import Path
import omni.ui as ui
from omni.ui import color as cl

# DB connection string -----------------------------------------

DB_KEY = "Driver={SQL Server}; Server=10.189.24.40; uid=rendering_dep; pwd=251_ee5FJK?58fde723c8cf9c!; Trusted_Connection=No;"

RENDER_STYLE_TABLE = "[ReportDB].[dbo].[vw_render_style_sku]"

#Brand Dictionary -----------------------------------------------

BRANDS_DICT = { "CD": "Dior Femme",
                "DM": "Dior Homme",
                "BP": "Barton Perreira",
                "BV": "Bulgari",
                "CL": "Celine",
                "FE": "Fendi",
                "GV": "Givenchy",
                "TH": "Tag Heuer",
                "VU": "Vuarnet",
                "LW": "Loewe",
                "KZ": "Kenzo",
                "LV": "Louis Vuitton"
                }

GENRES = [
            "Optical - Man",
            "Optical - Woman",
            "Sun - Man",
            "Sun - Woman",
            "All Man",
            "All Woman"
        ]

#Materials Dictionary -------------------------------------------

MAT_DICT = {
    "Utility": {
        "ID": {},
        "HDR": {},
        "Common_Mats": {},
    },
    "Acetate": {
        "Havana": {},
        "Opaline": {},
        "Solid": {},
        "Transparent": {},
    },
    "Injected": {
        "Solid": {},
        "Trasparent": {},
        "Opaline": {},
        "Havana": {},
        "Rubber": {},
    },
    "Metals": {
        "Brushed": {},
        "Sand_Blasted": {},
        "Shiny": {},
        "Matte": {},
        "Tumbled": {},
        "Satin": {},
    },
    "Lens": {
        "Gradient": {},
        "Solid": {},
    },
    "Fabric": {},
    "Varnish": {},
    "Gems": {
        "Strass": {},
        "Stones": {},
    },
    "Special": {
        "Carbon_Fiber": {},
        "Leather": {},
        "Cork": {}
    },
}
#Models init values ---------------------------------------------

DEFAULT_RELEASE = 262
START_FRAME = 1
END_FRAME = 8
SLIDER_VIEW = 1

#Sequence const -------------------------------------------------

SEQUENCE = True
SINGLE_FRAME = False

#Paths --------------------------------------------------------

#BLOB paths
BLOB_PATH = r"U:\01_USD"
BLOB_USD_PATH = r"U:\01_USD"
BLOB_USD_TEMPLATE_PATH = "U:\\02_TOOLS\\01_Template"
BLOB_CAMERAS_PATH = f"{BLOB_USD_TEMPLATE_PATH}\\cameras"

#USD templates filename
TEMPL_LIGHTS = "lights.usd"
TEMPL_LIMBO = "limbo.usd"

#BLOB_PATH = r"H:\\Prototyping_PD\\Rendering\\USDProject\\USD\\DIOR"
TEMPLATES_PATH = Path(__file__).parent.joinpath("tools","templates")
ICONS_PATH = Path(__file__).parent.joinpath("tools","style","icons")

#UI Visibility ------------------------------------------------

#When collapsed is True, the UI module will be hidden by default
IMPORT_TEMPLATE_UI_VISIBILITY = True
IMPORT_ALL_COLLECTION_UI_VISIBILITY = True
CUSTOM_IMPORT_TEMPLATE_UI_VISIBILITY = True
CUSTOM_MODEL_IMPORT_UI_VISIBILITY = True
RENDER_UI_VISIBILITY = True
VIEW_UI_VISIBILITY = True
MATERIALS_UI_VISIBILITY = False

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

WAIT_FRAMES = 300
ANTI_ALIASING_PATTERN = 3

# capture extensions settings

EXT = "png"
#EXT = "exr"
SAVE_ALPHA = True
PATH_TRACE_SPP = 256
PREROLL_FRAMES = 3

#USD variables ----------------------------------------------

CAMERA_TARGET = "/World/Setup/Cameras"
LIGHT_TARGET = "/World/Setup/Lights"
LIMBO_TARGET = "/World/Setup/Limbo"
WORLD_PATH = "/World"

SCOPES_TO_KEEP = [  "Models", 
                    "Setup", 
                    "Lights", 
                    "Cameras"
                ]

#Icons -------------------------------------------------------

FWD_FRAME_ICON = ICONS_PATH.joinpath("next_fr.png")
BACK_FRAME_ICON = ICONS_PATH.joinpath("prev_fr.png")
