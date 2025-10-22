import carb.settings

print("-"*20)

target_settings = ["movie", "movie_capture", "moviecapture"]

settings = carb.settings.get_settings()
dictionary = settings.get_settings_dictionary()

def print_render_settings(item, path=""):
    if hasattr(item, "get_keys"):
        for key in item.get_keys():
            sub_path = f"{path}/{key}" if path else f"/{key}"
            # Filtra subito solo le chiavi di render
            if any(word in sub_path for word in target_settings):
                value = settings.get(sub_path)
                print(f"{sub_path}: {value}")
            # Non effettua ricorsione per evitare errori di firma

print_render_settings(dictionary)
