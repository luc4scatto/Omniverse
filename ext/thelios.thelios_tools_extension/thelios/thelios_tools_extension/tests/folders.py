from pathlib import Path

base = Path(r"U:\03_MAT_LIBRARY\Thelios_Mat_Library")

folders = [
    # Common_Textures
    "Common_Textures/Bases",
    "Common_Textures/Dirt_Scratches/Metal",
    "Common_Textures/Dirt_Scratches/Acetate",
    "Common_Textures/Sand_Blasted",
    "Common_Textures/Tumbled",
    "Common_Textures/Brushed",
    "Common_Textures/Satin",
    "Common_Textures/Pattern",

    # Materials / Utility
    "Materials/Utility/ID",
    "Materials/Utility/HDR",
    "Materials/Utility/Common_Mats",

    # Materials / Acetate
    "Materials/Acetate/Havana/3627/Texture",
    "Materials/Acetate/Opaline",
    "Materials/Acetate/Solid",
    "Materials/Acetate/Transparent",
    "Materials/Acetate/MultiLayer",

    # Materials / Injected
    "Materials/Injected/Solid/Rubber",
    "Materials/Injected/Trasparent",
    "Materials/Injected/Opaline",
    "Materials/Injected/Havana/3627/Texture",

    # Materials / Metals
    "Materials/Metals/Brushed",
    "Materials/Metals/Sand_Blasted",
    "Materials/Metals/Shiny",
    "Materials/Metals/Matte",
    "Materials/Metals/Tumbled",
    "Materials/Metals/Satin",

    # Materials / Lens
    "Materials/Lens/Gradient/N5270",
    "Materials/Lens/Solid/A7080",

    # Other
    "Materials/Fabric",
    "Materials/Varnish",
    "Materials/Gems/Strass",
    "Materials/Gems/Stones",
    "Materials/Special/Carbon_Fiber/Texture",
]

for rel_path in folders:
    (base / rel_path).mkdir(parents=True, exist_ok=True)

print("Struttura creata sotto:", base.resolve())