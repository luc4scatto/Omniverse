# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import omni.ext
import omni.ui as ui
import omni.usd

import json
import sys
from pathlib import Path
import os

MAIN_PATH = Path(__file__).parent
SETTINGS_PATH = Path(__file__).parent.joinpath("settings")
TOOLS_PATH = Path(__file__).parent.joinpath("tools")
ICON_PATH = ""

query_res = ['DM40177I', ('01B', '261'), ('52N', '261'), ('57E', '261')]

json_path = f"{SETTINGS_PATH}\\settings.json"
#query_dir = TOOLS_PATH.joinpath("queries")
#style_dir = TOOLS_PATH.joinpath("style")

"""
print(f"---> Main path: {MAIN_PATH}")
print(f"---> Settings path: {SETTINGS_PATH}")
print(f"---> Json path: {json_path}")
print(f"---> Tools path: {TOOLS_PATH}")
print(f"---> Query path: {query_dir}")
"""

def load_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Errore: File di configurazione non trovato in {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Errore: File di configurazione non valido in {config_path}")
        return None

config = load_config(json_path)

#Paths from settings.json
if config:
    db_key = config["keys"]["db_key"]   #db key line
    genres = config["mode"]["genres"]  #list of genres
    ext_fld = config["paths"]["ext_dir"]  #list of genres

query_dir = f"{ext_fld}/tools/queries"
widget_add_dir = f"{ext_fld}/tools/widget_add"

sys.path.append(query_dir)
sys.path.append(widget_add_dir)

import brand_query, plm_query
#import tree_model

combo_elements = brand_query.pop_combo_brands(db_key) 


KIT_GREEN = 0xFF8A8777
LABEL_PADDING = 120

DARK_WINDOW_STYLE = {
    "Window": {"background_color": 0xFF444444},
    "Button": {"background_color": 0xFF292929, "margin": 3, "padding": 3, "border_radius": 2},
    "Button.Label": {"color": 0xFFCCCCCC},
    "Button:hovered": {"background_color": 0xFF9E9E9E},
    "Button:pressed": {"background_color": 0xC22A8778},
    "VStack::main_v_stack": {"secondary_color": 0x0, "margin_width": 10, "margin_height": 0},
    "VStack::frame_v_stack": {"margin_width": 15},
    "Rectangle::frame_background": {"background_color": 0xFF343432, "border_radius": 5},
    "Field::models": {"background_color": 0xFF23211F, "font_size": 14, "color": 0xFFAAAAAA, "border_radius": 4.0},
    "Frame": {"background_color": 0xFFAAAAAA},
    "Label::transform": {"font_size": 12, "color": 0xFF8A8777},
    "Circle::transform": {"background_color": 0x558A8777},
    "Field::transform": {
        "background_color": 0xFF23211F,
        "border_radius": 3,
        "corner_flag": ui.CornerFlag.RIGHT,
        "font_size": 12,
    },
    "Slider::transform": {
        "background_color": 0xFF23211F,
        "border_radius": 3,
        "draw_mode": ui.SliderDrawMode.DRAG,
        "corner_flag": ui.CornerFlag.RIGHT,
        "font_size": 14,
    },
    "Label::transform_label": {"font_size": 12, "color": 0xFFDDDDDD},
    "Label": {"font_size": 12, "color": 0xFF8A8777},
    "Label::label": {"font_size": 14, "color": 0xFF8A8777},
    "Label::title": {"font_size": 14, "color": 0xFFAAAAAA},
    "Triangle::title": {"background_color": 0xFFAAAAAA},
    "ComboBox::path": {"font_size": 12, "secondary_color": 0xFF23211F, "color": 0xFFAAAAAA},
    "ComboBox::choices": {
        "font_size": 12,
        "color": 0xFFAAAAAA,
        "background_color": 0xFF23211F,
        "secondary_color": 0xFF23211F,
    },
    "ComboBox:hovered:choices": {"background_color": 0xFF33312F, "secondary_color": 0xFF33312F},
    "Slider::value_less": {
        "font_size": 12,
        "color": 0x0,
        "border_radius": 5,
        "background_color": 0xFF23211F,
        "secondary_color": KIT_GREEN,
        "border_color": 0xFFAAFFFF,
        "border_width": 0,
    },
    "Slider::value": {
        "font_size": 14,
        "color": 0xFFAAAAAA,
        "border_radius": 5,
        "background_color": 0xFF23211F,
        "secondary_color": KIT_GREEN,
    },
    "Rectangle::add": {"background_color": 0xFF23211F},
    "Rectangle:hovered:add": {"background_color": 0xFF73414F},
    "CheckBox::greenCheck": {"font_size": 10, "background_color": KIT_GREEN, "color": 0xFF23211F},
    "CheckBox::whiteCheck": {"font_size": 10, "background_color": 0xFFDDDDDD, "color": 0xFF23211F},
    "Slider::colorField": {"background_color": 0xFF23211F, "font_size": 14, "color": 0xFF8A8777},
    # Frame
    "CollapsableFrame::standard_collapsable": {
        "background_color": 0xFF343432,
        "secondary_color": 0xFF343432,
        "font_size": 16,
        "border_radius": 2.0,
        "border_color": 0x0,
        "border_width": 0,
    },
    "CollapsableFrame:hovered:standard_collapsable": {"secondary_color": 0xFFFBF1E5},
    "CollapsableFrame:pressed:standard_collapsable": {"secondary_color": 0xFFF7E4CC},
}

CollapsableFrame_style = {
    "CollapsableFrame": {
        "background_color": 0xFF343432,
        "secondary_color": 0xFF343432,
        "color": 0xFFAAAAAA,
        "border_radius": 4.0,
        "border_color": 0x0,
        "border_width": 0,
        "font_size": 14,
        "padding": 8,
    },
    "HStack::header": {"margin": 10},
    "CollapsableFrame:hovered": {"secondary_color": 0xFF3A3A3A},
    "CollapsableFrame:pressed": {"secondary_color": 0xFF343432},
}

class TheliosExtension(omni.ext.IExt):
    def __init__(self):
        super().__init__()
        
        self._stage = omni.usd.get_context().get_stage()
        self.brand_combo = None
        self.type_combo = None
        self.release_field = None
        
        self._editor_window = None
        self._window_Frame = None
        
        self.int_model = ui.SimpleIntModel(262)
        self.model_model = ui.SimpleStringModel()
        self.brand_string_model = ui.SimpleStringModel()
        self.type_string_model = ui.SimpleStringModel()
        
        self.show_labels = False
        self.checkbox_data = []
                
    def set_style_dark(self):
        self._window_Frame.set_style(DARK_WINDOW_STYLE)
        
    def _build_dropdown_frame(self):
        with ui.Frame():
            with ui.ZStack():
                ui.Rectangle(name="frame_background")
                with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                    ui.Spacer(height=5)
                    
                    with ui.HStack():
                        ui.Label("Release", name="label", width=LABEL_PADDING)
                        
                        self.release_field = ui.IntField(self.int_model, height=10, name="release")
                        self._create_control_state()
                        
                    with ui.HStack():
                        ui.Label("Brand", name="label", width=LABEL_PADDING)
                        self.brand_combo = ui.ComboBox(1, *combo_elements, height=10, name="brand_choices").model
                        self._create_control_state()
                    with ui.HStack():
                        ui.Label("Type", name="label", width=LABEL_PADDING)
                        self.type_combo = ui.ComboBox(0, *genres, height=10, name="type_choices").model
                        self._create_control_state()
                        
                    self.import_btn = ui.Button("Import")
                    ui.Spacer(height=0)
                    
    def _create_control_state(self, state=0):
        control_type = [
            f"{ICON_PATH}/Expression.svg",
            f"{ICON_PATH}/Mute Channel.svg",
            f"{ICON_PATH}/mixed properties.svg",
            f"{ICON_PATH}/Default value.svg",
            f"{ICON_PATH}/Changed value.svg",
            f"{ICON_PATH}/Animation Curve.svg",
            f"{ICON_PATH}/Animation Key.svg",
        ]
        
        if state == 0:
            ui.Circle(name="transform", width=20, radius=3.5, size_policy=ui.CircleSizePolicy.FIXED)
        else:
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Image(control_type[state - 1], width=20, height=12)
                ui.Spacer()
                
    def _create_checkbox_control(self, name, value, label_width=100, line_width=ui.Fraction(1)):
        with ui.HStack():
            ui.Label(name, name="label", width=0)
            ui.Spacer(width=10)
            ui.Line(style={"color": 0x338A8777}, width=line_width)
            ui.Spacer(width=5)
            with ui.VStack(width=10):
                ui.Spacer()
                ui.CheckBox(width=10, height=0, name="greenCheck").model.set_value(value)
                ui.Spacer()
            self._create_control_state(0)
            
    def _create_path_combo(self, name, paths):
        with ui.HStack():
            ui.Label(name, name="label", width=LABEL_PADDING)
            with ui.ZStack():
                ui.StringField(name="models").model.set_value(paths)
                with ui.HStack():
                    ui.Spacer()
                    #ui.Circle(width=10, height=20, style={"background_color": 0xFF555555})
            ui.ComboBox(0, paths, paths, name="path", width=0, height=0, arrow_only=True)
            ui.Spacer(width=5)
            ui.Image("resources/icons/folder.png", width=15)
            ui.Spacer(width=5)
            ui.Image("resources/icons/find.png", width=15)
            self._create_control_state(2)
            
    def _get_plm_data(self):
        brand_model = self.brand_combo.get_item_value_model()
        brand_index = brand_model.as_int
        brand_value = combo_elements[brand_index]
        
        type_model = self.type_combo.get_item_value_model()
        type_index = type_model.as_int
        type_value = genres[type_index]
        
        season_value = self.int_model.get_value_as_int()
        
        print(f"+++ Season: {season_value}")
        print(f"--- Brand: {brand_value}")
        print(f"*** Type: {type_value}")
        
        if type_value == "All Woman":
            res_query_optical_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Woman")
            res_query_sun_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Woman")
            
            res_query_sun = list(set(res_query_optical_woman).union(set(res_query_sun_woman)))
            sorted_list = sorted(res_query_sun, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        elif type_value == "All Man":
            res_query_optical_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Man")
            res_query_sun_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Man")
            
            result_query_man = list(set(res_query_optical_man).union(set(res_query_sun_man)))
            sorted_list = sorted(result_query_man, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        else:
            res_query = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),str(type_value))
            print(res_query)
            return res_query
        
    def _get_sku_model_plm(self):
        model_value = self.model_model.get_value_as_string()
        model_sku_res = plm_query.get_sku_model_plm(db_key, str(model_value))
        return model_sku_res
    
    def _build_scrolling_content(self):
        
        self.checkbox_data = []  # Reset dei dati
        sku_rel_list = self._get_sku_model_plm()
        
        if self.show_labels:
            with ui.VStack(spacing=10):
                for item in sku_rel_list:
                    with ui.HStack():
                        style_label = ui.Label(item[2], width=100, height=30) #Style name
                        sku_label = ui.Label(item[0], width=100, height=30) #SKU
                        release_label = ui.Label(item[1], width=100, height=30) #Release
                        checkbox = ui.CheckBox(width=12, height=12)
                        
                        self.checkbox_data.append({
                            'checkbox': checkbox,
                            'sku': item[0],
                            'release': item[1]
                        })
                
        #self.scroll_frame.rebuild()
        
    def _on_button_click(self):
        self.show_labels = True
        self.scroll_frame.rebuild()  # Aggiorna il contenuto dello ScrollingFrame
        
    def _get_selected_items(self):
        
        selected_items = [
            (data['sku'], data['release']) 
            for data in self.checkbox_data 
            if data['checkbox'].model.get_value_as_bool()
        ]
        
        print(f"Elementi selezionati: {selected_items}")
        return selected_items
        
    def _import_custom_model(self):
        """Crea l'interfaccia per l'importazione del modello con la tabella"""
        # Custom Collapsable Frame
        with ui.CollapsableFrame(title="Custom Model Import ", style=CollapsableFrame_style):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                with ui.HStack(spacing=5):
                    ui.Label("Model", name="label", width=50)
                    
                    self.model_field = ui.StringField(self.model_model, height=10, name="model")
                    self.import_custom_button = ui.Button("Import Model", height=10, clicked_fn=self._on_button_click)
                
                ui.Spacer(height=2)
                
                # Container principale per la tabella
                with ui.VStack(spacing=0):
                    # Intestazioni della tabella
                    with ui.HStack(height=30):
                        ui.Label("MODEL NAME", width=100, style={"font_weight": "bold"})
                        ui.Label("SKU", width=100, style={"font_weight": "bold"})
                        ui.Label("RELEASE", width=100, style={"font_weight": "bold"})
                        ui.Label("IMPORT", width=100, style={"font_weight": "bold"})
                    
                    # Separatore
                    ui.Rectangle(height=1, style={"background_color": 0xFF555555})
                    ui.Spacer(height=2)
                    
                    # ScrollingFrame con il Frame interno per il contenuto
                    self.scroll_frame = ui.ScrollingFrame(
                        height=200,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON
                    )
                    
                    self.scroll_frame.set_build_fn(self._build_scrolling_content)
                    
                    ui.Spacer(height=2)
                    
                    self.get_checkbox_data = ui.Button("Get Selected", height=10, clicked_fn=self._get_selected_items)
                    
                    ui.Spacer(height=16)
            
    def on_startup(self, _ext_id):
        """ build the window for the Class"""
        self.width = 450
        self.height = 500
        
        self._editor_window = ui.Window("Thelios USD Tools", width=self.width, height=self.height)
        self._editor_window.deferred_dock_in("Layers")
        self._editor_window.setPosition(450, 100)
        self._editor_window.frame.set_style(DARK_WINDOW_STYLE)
        with self._editor_window.frame:
            with ui.VStack():
                ui.Spacer(height=10)
                self._window_Frame = ui.ScrollingFrame(
                    name="canvas",
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                )
                with self._window_Frame:
                    with ui.VStack(height=0, name="main_v_stack", spacing=6):
                        
                        # DropDown Frame
                        self._build_dropdown_frame()
                        
                        # Crea la tabella SKU-RELEASE
                        self._import_custom_model()
                        
                        #self.scroll_frame.set_build_fn(self._build_scrolling_content)
                        
                        #self._test_scroll_frame()
                        #self.button_test = ui.Button("Test Scroll")
                        
                        # Custom Collapsable Frame
                        with ui.CollapsableFrame(title="Optional USD Selection Folder ", style=CollapsableFrame_style):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                ui.Spacer(height=0)
                                self._create_path_combo("UI Path", "omni:/Project/Cool_ui.usd")
                                ui.Spacer(height=0)
                                
                        # Custom Collapsable Frame
                        with ui.CollapsableFrame(title="Images Options", collapsed=True, style=CollapsableFrame_style):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                self._create_path_combo("Images Path", "omni:/Library/Images/")
                                ui.Spacer(height=0)
                                
        self.import_btn.set_clicked_fn(self._get_plm_data)
        #self.import_custom_button.set_clicked_fn(self._on_button_click)
        # Il pulsante import_custom_button è già collegato alla funzione _refresh_table nel metodo _import_custom_model
        
        return self._editor_window
        
    def on_shutdown(self):
        self._editor_window = None
