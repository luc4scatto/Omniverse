# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

"""
Thelios USD Tools Extension for NVIDIA Omniverse

This extension provides a comprehensive interface for managing USD assets within NVIDIA Omniverse,
specifically designed for the Thelios product line. It includes functionality for:
- Database integration with PLM (Product Lifecycle Management) systems
- Dynamic UI creation with brand/type/release selection
- SKU management and batch import operations
- USD hierarchy creation and payload management
- Custom styling and collapsible UI components

The extension follows the standard Omniverse Kit extension pattern by inheriting from omni.ext.IExt
and implementing the required startup/shutdown lifecycle methods.

Dependencies:
    - omni.ext: Omniverse extension framework
    - omni.ui: Omniverse UI toolkit for interface creation
    - omni.usd: USD context and stage management
    - pxr: Pixar USD Python bindings
    - External modules: brand_query, plm_query, style_widgets, usd_tools

Configuration:
    The extension reads configuration from a JSON file located at settings/settings.json
    which contains database keys, paths, and genre definitions.

Author: [Luca Scattolin - Thelios]
Version: 1.0
License: SPDX-License-Identifier: LicenseRef-NvidiaProprietary
Copyright: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
"""


import omni.ext
import omni.ui as ui
from omni.kit.window.filepicker import FilePickerDialog
import omni.usd
from omni.ui import color as cl
from pxr import Usd, UsdGeom, Sdf
from omni.kit.notification_manager import post_notification, NotificationStatus

import json
import sys
from pathlib import Path
import os

# Configuration constants
MAIN_PATH = Path(__file__).parent
SETTINGS_PATH = Path(__file__).parent.joinpath("settings")
TOOLS_PATH = Path(__file__).parent.joinpath("tools")
ICON_PATH = ""
LABEL_PADDING = 70

RESOLUTIONS = (
    "1920x1920",
    "2048x2048",
    "4096x4096")

json_path = f"{SETTINGS_PATH}\\settings.json"

def load_config(config_path: str) -> dict:
    """
    Load configuration from JSON file.
    
    Reads and parses the extension's configuration file containing database
    credentials, file paths, and application settings.
    
    Args:
        config_path (str): Path to the JSON configuration file
        
    Returns:
        dict or None: Parsed configuration dictionary if successful, None on error
        
    Example:
        >>> config = load_config("settings/settings.json")
        >>> if config:
        ...     db_key = config["keys"]["db_key"]
    """
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid configuration file at {config_path}")
        return None

# Load configuration and setup paths
config = load_config(json_path)

# Extract paths from settings.json
if config:
    db_key = config["keys"]["db_key"]     # Database key line
    genres = config["mode"]["genres"]      # List of genres
    ext_fld = config["paths"]["ext_dir"]   # Extension directory
    
templates_dir = f"{ext_fld}\\tools\\templates"

from .tools.queries import brand_query, plm_query
from .tools.style import style_widgets
from .tools.templates import template_tools
from .tools.usd import usd_tools
from .tools.render import render_settings, render_launch

# Setup UI styles
DARK_WINDOW_STYLE = style_widgets.window_style()
CollapsableFrame_style = style_widgets.collapbsable_style()

# Initialize brand combo elements
combo_elements = brand_query.pop_combo_brands(db_key) 

class TheliosExtension(omni.ext.IExt):
    """
    Main extension class for Thelios USD Tools.
    
    This class implements the core functionality of the Thelios extension,
    providing a comprehensive UI for managing USD assets, database integration,
    and batch import operations. It inherits from omni.ext.IExt following
    the standard Omniverse extension pattern.
    
    The extension creates a multi-panel interface with:
    - Brand/Type/Release selection dropdowns
    - Custom model import with SKU selection table 
    - Optional USD path configuration
    - Image options management
    
    Attributes:
        _stage (Usd.Stage): Reference to the current USD stage
        brand_combo (ui.AbstractItemModel): Brand selection combo box model
        type_combo (ui.AbstractItemModel): Type selection combo box model
        release_field (ui.IntField): Release number input field
        _editor_window (ui.Window): Main extension window
        _window_Frame (ui.ScrollingFrame): Main scrolling container
        int_model (ui.SimpleIntModel): Model for integer release values
        model_model (ui.SimpleStringModel): Model for model name strings
        brand_string_model (ui.SimpleStringModel): Model for brand strings
        type_string_model (ui.SimpleStringModel): Model for type strings
        show_labels (bool): Flag to control SKU table visibility
        checkbox_data (list): Storage for checkbox states and associated SKU data
    """
    
    def __init__(self):
        """
        Initialize the extension with default values and UI models.
        
        Sets up all necessary UI models, references to USD stage,
        and initializes internal state variables.
        """
        super().__init__()
        
        self._stage = omni.usd.get_context().get_stage()
        self.brand_combo = None
        self.type_combo = None
        self.release_field = None
        self.resolution_combo = None
        
        self._editor_window = None
        self._window_Frame = None
        
        # UI Data models
        self.int_model = ui.SimpleIntModel(262)
        self.frame_model = ui.SimpleIntModel(8)
        self.int_filter_model = ui.SimpleIntModel(262)
        self.model_model = ui.SimpleStringModel()
        self.brand_string_model = ui.SimpleStringModel()
        self.type_string_model = ui.SimpleStringModel()
        
        self.startfr_model = ui.SimpleIntModel(1)
        self.endfr_model = ui.SimpleIntModel(8)
        self.singlefr_model = ui.SimpleIntModel(1)
        
        self.sequence_model = ui.SimpleBoolModel(True)
        
        self._timeline = omni.timeline.get_timeline_interface()
        self._current_fps = self._timeline.get_time_codes_per_seconds()
        
        # State management
        self.show_labels = False
        self.checkbox_data = []
        self.apply_filter = False  # Flag for filtering state
                
    def set_style_dark(self):
        """
        Apply dark theme styling to the main window frame.
        
        This method applies the predefined dark window style to the main
        window frame for consistent visual appearance.
        """
        self._window_Frame.set_style(DARK_WINDOW_STYLE)
        
    def _dropdown_import_template_UI(self):
        with ui.CollapsableFrame(title="Import Template Scene ", style=CollapsableFrame_style):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                def like_radio(model, first, second):
                    """Turn on the model and turn off two checkboxes"""
                    if model.get_value_as_bool():
                        model.set_value(True)
                        first.model.set_value(False)
                        second.model.set_value(False)
                        
                #ui.Spacer(height=2)    
                
                with ui.HStack(spacing=12):
                    with ui.HStack():
                        abc_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("ABC", name="label")
                        
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})  
                    
                    with ui.HStack():
                        configurator_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Configurator", name="label")
                        
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})  
                    
                    with ui.HStack():
                        site_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Site", name="label")
                        
                    configurator_checkbox.model.add_value_changed_fn(lambda a, b=abc_checkbox, c=site_checkbox: like_radio(a, b, c))
                    abc_checkbox.model.add_value_changed_fn(lambda a, b=configurator_checkbox, c=site_checkbox: like_radio(a, b, c))
                    site_checkbox.model.add_value_changed_fn(lambda a, b=configurator_checkbox, c=abc_checkbox: like_radio(a, b, c))
                    
                    abc_checkbox.model.set_value(True)
                    
                def on_import_click():
                    if abc_checkbox.model.get_value_as_bool():
                        print("Import: ABC selezionato")
                        template_tools._import_camera(self._stage, "Brand")
                        
                    elif configurator_checkbox.model.get_value_as_bool():
                        print("Import: Configurator selezionato")
                        template_tools._import_lights(self._stage)
                        
                    elif site_checkbox.model.get_value_as_bool():
                        print("Import: Site selezionato")
                        template_tools._import_limbo(self._stage)
                    else:
                        print("Import: nessuna opzione selezionata")
                        
                self.import_template_btn = ui.Button("Import Template", name="import_template", clicked_fn=on_import_click)
                
    def _dropdown_custom_model_UI(self):
        
        """
        Create the custom model import interface.
        
        Builds a collapsible frame containing:
        - Model name input field
        - "Select Model" button to query PLM data
        - Table headers for SKU display
        - Scrollable area for SKU selection checkboxes
        - "Import selected SKUs" button for batch processing
        
        This interface allows users to manually specify a model name
        and then select specific SKUs for import rather than using
        the dropdown-based selection method.
        """
        
        
        # Custom Collapsable Frame
        with ui.CollapsableFrame(title="Custom Model Import ", style=CollapsableFrame_style, collapsed=True):
            with ui.VStack(height=0, spacing=15, name="frame_v_stack"):
                # Model input and select button
                with ui.HStack(spacing=10, alignment=ui.Alignment.V_CENTER):
                    ui.Label("Model", name="label", width=LABEL_PADDING)
                    self.model_field = ui.StringField(self.model_model, name="model", height=10, style={"margin":3})
                    self.import_custom_button = ui.Button("Select Model", clicked_fn=self._import_sel_skus, name="select_model")
                    
                with ui.ZStack():
                    ui.Rectangle(style={"background_color": cl(0.25), 
                                        "padding": 8, 
                                        "border_radius": 2, 
                                        "margin": -4} )  
                    
                    with ui.HStack(height=0, spacing=10, alignment=ui.Alignment.V_CENTER):
                        ui.Label("Rel Filter", name="label", width=LABEL_PADDING)
                        self.season_field = ui.StringField(self.int_filter_model, name="filter", style={"margin":3})
                        self.filter_button = ui.Button("Filter", clicked_fn=self._filter_skus)
                        self.clear_filter_button = ui.Button("Clear Filter", clicked_fn=self._clear_filter, name="clear_filter", style= {})
                        
                """    
                # Aggiungi anche un pulsante per rimuovere il filtro
                with ui.HStack():
                    ui.Label("", width=LABEL_PADDING)  # Spacer per allineamento
                    ui.Spacer()  # Per allineare a sinistra
                """
                
                ui.Spacer(height=1)
                
                # Main container for the table
                with ui.VStack(spacing=0):
                    # Table headers
                    with ui.HStack():
                        ui.Label("NAME", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        ui.Label("SKU", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        ui.Label("RELEASE", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        ui.Label("IMPORT", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                    
                    ui.Spacer(height=4)
                    
                    # ScrollingFrame with internal Frame for content
                    self.scroll_frame = ui.ScrollingFrame(
                        height=200,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
                    
                    # Set build function for dynamic content
                    self.scroll_frame.set_build_fn(self._build_scrolling_content)
                    
                    ui.Spacer(height=16)
                    with ui.HStack():
                        # Import button for selected SKUs
                        self.create_hierarchy_button = ui.Button("Import selected SKUs", 
                                                                height=10, 
                                                                clicked_fn=self._create_hierarchy_and_import_payload,
                                                                name="import_selected")
                        
                        self.clear_button = ui.Button("Clear", 
                                                                height=10, 
                                                                clicked_fn=self._clear_all,
                                                                name = "clear_scrolling")
                    
                    ui.Spacer(height=8)
                
    def _dropdown_import_custom_template_scene_UI(self):
        
        with ui.CollapsableFrame(title="Custom Import Template Scene ", style=CollapsableFrame_style):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                    
                # Brand selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Camera Selection", name="label", width=LABEL_PADDING)
                    self.brand_camera_combo = ui.ComboBox(1, *combo_elements, height=10, name="camera_brand").model
                    #self._create_control_state()
                    
                ui.Spacer(height=2)    
                
                with ui.HStack(spacing=12):
                    with ui.HStack():
                        camera_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Camera", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})    
                    
                    with ui.HStack():
                        lights_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Lights", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})    
                    
                    with ui.HStack():
                        limbo_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Limbo", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})    
                    
                    with ui.HStack():
                        settings_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Settings", name="label")
                        
                    
                    def import_camera(stage):
                        print("--- Import: Camera ---")
                        brand_camera_model = self.brand_camera_combo.get_item_value_model()
                        template_tools._import_camera(stage, brand_camera_model, combo_elements, templates_dir)
                        
                    def import_lights(stage):
                        print("--- Import: Lights ---")
                        template_tools._import_lights(stage, templates_dir)
                        
                    def import_limbo(stage):
                        print("--- Import: Limbo ---")
                        template_tools._import_limbo(stage, templates_dir)
                        
                    def import_settings():
                        print("--- Import: Settings ---")
                        render_settings.import_render_settings()
                        
                    def on_import_click():
                        
                        stage = omni.usd.get_context().get_stage()
                        
                        if camera_checkbox.model.get_value_as_bool():
                            import_camera(stage)
                            
                        if lights_checkbox.model.get_value_as_bool():
                            import_lights(stage)
                            
                        if limbo_checkbox.model.get_value_as_bool():
                            import_limbo(stage)
                            
                        if settings_checkbox.model.get_value_as_bool():
                            import_settings()
                            
                        if not any([
                            camera_checkbox.model.get_value_as_bool(),
                            lights_checkbox.model.get_value_as_bool(),
                            limbo_checkbox.model.get_value_as_bool(),
                            settings_checkbox.model.get_value_as_bool()
                        ]):
                            post_notification(
                                "No checkbox selected!",
                                duration=5,
                                status=NotificationStatus.WARNING
                            )
                            print("Import completed")
                            
                        #Uncheck values
                            
                        camera_checkbox.model.set_value(False),
                        lights_checkbox.model.set_value(False),
                        limbo_checkbox.model.set_value(False),
                        settings_checkbox.model.set_value(False)
                            
                    def on_import_click_all():
                        
                        stage = omni.usd.get_context().get_stage()
                        
                        print("--- Import: All ---")
                        
                        import_camera(stage)
                        import_lights(stage)
                        import_limbo(stage)
                        import_settings()
                        
                        camera_checkbox.model.set_value(False),
                        lights_checkbox.model.set_value(False),
                        limbo_checkbox.model.set_value(False),
                        settings_checkbox.model.set_value(False)
                        
                        post_notification(
                            "Import completed!",
                            duration=5,
                            status=NotificationStatus.INFO
                        )
                        print("Import completed")
                    
                # Import button
                self.import_temp_item_btn = ui.Button("Import Selected", clicked_fn=on_import_click, name="import_collection")
                
                ui.Rectangle(height=1, style={"background_color": cl(0.3), "margin": 0})
                
                self.import_all_temp_item_btn = ui.Button("Import All", clicked_fn=on_import_click_all, name="import_collection")
                
    def _dropdown_all_collection_UI(self):
        """
        Create the main dropdown selection frame.
        
        Builds the top section of the UI containing:
        - Release number input field
        - Brand selection dropdown (populated from database)
        - Type/Genre selection dropdown
        - Import button to trigger PLM data retrieval
        
        This frame serves as the primary input interface for filtering
        and selecting product data from the PLM system.
        """
        with ui.CollapsableFrame(title="All Collection Import ", style=CollapsableFrame_style, collapsed=True):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                # Release input field
                with ui.HStack(spacing=10):
                    ui.Label("Release", name="label", width=LABEL_PADDING)
                    self.release_field = ui.IntField(self.int_model, height=10, name="release")
                    #self._create_control_state()
                    
                # Brand selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Brand", name="label", width=LABEL_PADDING)
                    self.brand_combo = ui.ComboBox(1, *combo_elements, height=10, name="brand_choices").model
                    #self._create_control_state()
                    
                # Type/Genre selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Type", name="label", width=LABEL_PADDING)
                    self.type_combo = ui.ComboBox(0, *genres, height=10, name="type_choices").model
                    #self._create_control_state()
                    
                # Import button
                self.import_btn = ui.Button("Import", clicked_fn=self._get_plm_data, name="import_collection")
                ui.Spacer(height=0)
                
    def _dropdown_render_UI(self):
        
        slider_enabled_style = {
            "background_color": 0xFF23211F,
            "secondary_color": cl(0.6),
            "color": cl(0.9),
            "draw_mode": ui.SliderDrawMode.HANDLE
            #"border_color": cl(0.2),
            #"border_width": 2
        }
        slider_disabled_style = {
            "background_color": cl(0.5),
            "secondary_color": cl(0.6),
            "color": cl(0.7),
            "draw_mode": ui.SliderDrawMode.HANDLE
        }
        
        def like_radio(model, first):
            """Turn on the model and turn off two checkboxes"""
            if model.get_value_as_bool():
                model.set_value(True)
                first.model.set_value(False)
                
        def on_checkbox_changed(checkbox_model, slider):
            slider.enabled = checkbox_model.get_value_as_bool()
            # Cambia lo stile in base allo stato
            if slider.enabled:
                slider.style = slider_enabled_style
            else:
                slider.style = slider_disabled_style
                        
        def on_folder_selected(dialog, filename, dirname):
            # Solo cartella selezionata
            dialog.hide()
            export_path_field.model.set_value(dirname)
        
        def on_folder_icon_click():
            # Apertura FilePicker solo per cartelle
            dialog = FilePickerDialog(
                "Seleziona cartella di export",
                apply_button_label="Seleziona",
                click_apply_handler=lambda filename, dirname: on_folder_selected(dialog, filename, dirname),
                select_folder=True  # Opzione solo cartella!
            )
            dialog.show()
        
        with ui.CollapsableFrame(title="Render", style=CollapsableFrame_style, collapsed=False):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                with ui.HStack(spacing=10):
                    
                    ui.Label("Exp. Path", name="label", width=LABEL_PADDING)
                    
                    export_path_field = ui.StringField(self.type_string_model, name="export_path", height=10)
                    ui.Button(name="Scegli cartella", 
                            image_url="resources/icons/folder.png", 
                            alignemnt=ui.Alignment.TOP,
                            width=28,
                            height=28,
                            clicked_fn=on_folder_icon_click,
                            style={"margin":3, "background_color": cl(0)})
                    #self._create_control_state()
                    
                with ui.HStack(spacing=10):
                    ui.Label("Resolution", name="label", width=LABEL_PADDING)
                    self.resolution_combo = ui.ComboBox(0, *RESOLUTIONS, height=10, name="type_choices").model
                    #self._create_control_state()
                    
                with ui.HStack():
                    
                    sequence_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35),"margin":6},
                                            model=self.sequence_model,
                                            name="sequence_checkbox")
                    ui.Label("Sequence", name="label")
                    
                    single_checkbox = ui.CheckBox(width=36, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35),"margin":6},
                                            name="single_checkbox")
                    ui.Label("Single", name="label")
                    
                    sequence_checkbox.model.add_value_changed_fn(lambda a, b=single_checkbox: like_radio(a, b))
                    single_checkbox.model.add_value_changed_fn(lambda a, b=sequence_checkbox: like_radio(a, b))
                    
                    
                ui.Rectangle(height=1, style={"background_color": cl(0.3), "margin": 0})
                
                with ui.HStack(spacing=10):
                    ui.Label("Start/End", name="label", width=LABEL_PADDING)
                    self.start_slider = ui.IntSlider(min=1, max=8, step=1)
                    self.start_slider.model = self.startfr_model
                    self.start_slider.enabled = True # parte disattivato
                    
                    self.end_slider = ui.IntSlider(min=1, max=8 ,step=1)
                    self.end_slider.model = self.endfr_model
                    self.end_slider.enabled = True # parte disattivato
                    #self._create_control_state()
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0}) 
                    
                    ui.Label("Single Frame", name="label", width=LABEL_PADDING)
                    self.single_slider = ui.IntSlider(min=1, max=8 ,step=1, style=slider_disabled_style)
                    self.single_slider.model = self.singlefr_model
                    self.single_slider.enabled = False # parte disattivato
                    #self._create_control_state()
                    
                sequence_checkbox.model.add_value_changed_fn(lambda model: on_checkbox_changed(model, self.start_slider))  
                sequence_checkbox.model.add_value_changed_fn(lambda model: on_checkbox_changed(model, self.end_slider))  
                single_checkbox.model.add_value_changed_fn(lambda model: on_checkbox_changed(model, self.single_slider))
                    
                self.render_btn = ui.Button("Render", clicked_fn=self._render_sequence, name="render_sequence")
                
    def _create_control_state(self, state=0):
        """
        Create visual control state indicators.
        
        Generates small visual indicators (circles or icons) next to UI controls
        to show their current state. Used for visual feedback and status indication.
        
        Args:
            state (int): State indicator type (0-6)
                        0: Default circle indicator
                        1-6: Various icon states for different control states
        """
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
                
    def _create_checkbox_control(self, name: str, value: bool, label_width=100, line_width=ui.Fraction(1)):
        """
        Create a checkbox control with label and visual line.
        
        Builds a horizontal layout containing a label, decorative line,
        and checkbox for boolean value selection. Used in property panels
        and option selections.
        
        Args:
            name (str): Display name for the checkbox
            value (bool): Initial checkbox state
            label_width (int, optional): Width of the label in pixels. Defaults to 100
            line_width (ui.Fraction, optional): Width of decorative line. Defaults to ui.Fraction(1)
        """
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
            
    def _create_path_combo(self, name: str, paths):
        """
        Create a path selection combo box with browser icons.
        
        Builds a composite control for file/path selection containing:
        - Label for the path type
        - String field showing current path
        - Dropdown for path selection
        - Folder and search icons for file browsing
        
        Args:
            name (str): Display label for the path selector
            paths (str or list): Available path options
        """
        with ui.HStack():
            ui.Label(name, name="label", width=LABEL_PADDING)
            with ui.ZStack():
                ui.StringField(name="models").model.set_value(paths)
                with ui.HStack():
                    ui.Spacer()
            ui.ComboBox(0, paths, paths, name="path", width=0, height=0, arrow_only=True)
            ui.Spacer(width=5)
            ui.Image("resources/icons/folder.png", width=15)
            ui.Spacer(width=5)
            ui.Image("resources/icons/find.png", width=15)
            self._create_control_state(2)
            
    def _get_plm_data(self) -> list:
        """
        Retrieve product data from PLM system based on current selections.
        
        Extracts values from the UI dropdowns (brand, type, release) and
        queries the PLM database for matching products. Handles special
        cases for "All Woman" and "All Man" types by combining multiple
        queries for optical and sun categories.
        
        Returns:
            list: Sorted list of tuples containing product data (SKU, Release, etc.)
                    Returns combined results for "All" categories, single query results otherwise

        Example:
            >>> data = self._get_plm_data()
            >>> # Returns: [('SKU001', 'v1.0', 'Style1'), ('SKU002', 'v1.1', 'Style2')]
        """
        # Extract current selections from UI
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
        
        # Handle combined queries for "All Woman" category
        if type_value == "All Woman":
            res_query_optical_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Woman")
            res_query_sun_woman = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Woman")
            
            res_query_sun = list(set(res_query_optical_woman).union(set(res_query_sun_woman)))
            sorted_list = sorted(res_query_sun, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        # Handle combined queries for "All Man" category
        elif type_value == "All Man":
            res_query_optical_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Optical - Man")
            res_query_sun_man = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),"Sun - Man")
            
            result_query_man = list(set(res_query_optical_man).union(set(res_query_sun_man)))
            sorted_list = sorted(result_query_man, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        # Handle single category queries
        else:
            res_query = plm_query.get_plm_data(db_key,str(season_value),str(brand_value),str(type_value))
            print(res_query)
            return res_query
        
    def _get_sku_model_plm(self):
        """
        Retrieve SKU and model data from PLM for the specified model.
        
        Queries the PLM system for all SKUs associated with the currently
        entered model name. Used to populate the SKU selection table.
        
        Returns:
            list: List of tuples containing (SKU, Release, Style) data
                    for the specified model
        """
        model_value = self.model_model.get_value_as_string()
        model_sku_res = plm_query.get_sku_model_plm(db_key, str(model_value))
        return model_sku_res
    
    def _build_scrolling_content(self):
        """
        Build the scrollable content for SKU selection table with optional filtering.
        
        Creates a dynamic table showing available SKUs for the selected model.
        Can filter results based on release value if filter is applied.
        Each row contains:
        - Style name (in green highlight color)
        - SKU identifier
        - Release version
        - Selection checkbox
        
        The table is populated based on PLM query results and includes
        checkbox state management for batch operations.
        """
        self.checkbox_data = []  # Reset data storage
        sku_rel_list = self._get_sku_model_plm()
        
        # Apply filter if filter value is set
        if hasattr(self, 'apply_filter') and self.apply_filter:
            filter_value = self.int_filter_model.get_value_as_string().strip()
            if filter_value:
                # Filter tuples where the second element (release) contains the filter value
                sku_rel_list = [item for item in sku_rel_list if filter_value in str(item[1])]
                print(f"Filtered results for release containing '{filter_value}': {len(sku_rel_list)} items")
        
        if self.show_labels:
            with ui.VStack(spacing=0):
                for item in sku_rel_list:
                    with ui.HStack():
                        # Style name in green
                        style_label = ui.Label(item[2],
                                                height=16, 
                                                style={"font_size":14, "color":cl("#77b901")}, 
                                                alignment=ui.Alignment.CENTER)
                        # SKU identifier
                        sku_label = ui.Label(item[0], 
                                            height=16, 
                                            style={"font_size":16}, 
                                            alignment=ui.Alignment.CENTER)
                        # Release version
                        release_label = ui.Label(item[1], 
                                                height=16, 
                                                style={"font_size":16}, 
                                                alignment=ui.Alignment.CENTER)
                        
                        ui.Spacer()
                        # Selection checkbox
                        checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        
                        # Store checkbox reference and associated data
                        self.checkbox_data.append({
                            'checkbox': checkbox,
                            'sku': item[0],
                            'release': item[1]
                        })
        
    def _import_sel_skus(self):
        """
        Trigger the display of SKU selection interface.
        
        Sets the flag to show the SKU table labels and triggers a rebuild
        of the scrolling frame to display the available SKUs for selection.
        This method is called when the "Select Model" button is clicked.
        """
        self.show_labels = True
        self.scroll_frame.rebuild()  # Update ScrollingFrame content
        
    def _render_sequence(self):
        
        export_path = self.type_string_model.get_value_as_string()
        
        start_frame = self.startfr_model.get_value_as_int()
        end_frame = self.endfr_model.get_value_as_int()
        
        single_frame = self.singlefr_model.get_value_as_int()
        
        resolution_model = self.resolution_combo.get_item_value_model()
        
        res_index = resolution_model.as_int
        res_value = RESOLUTIONS[res_index]
        
        sing_seq=True
        
        print(f"Export Path: {export_path}")
        print(f"Resolution: {res_value}")
        print(f"Start Frame: {start_frame}")        
        print(f"End Frame: {end_frame}")
        print(f"Single Frame: {single_frame}")
        
        render_launch.render_launch_png(res_value,
                                        export_path,
                                        sing_seq,
                                        start_frame, 
                                        end_frame, 
                                        single_frame)
        
        #render_tools.capture_sequence_movie(export_path, "frame", num_frames )
    
    def _filter_skus(self):
        """
        Apply filter to SKU results based on release value.
        
        Sets the filter flag and triggers a rebuild of the scrolling frame
        to display only SKUs that match the filter criteria.
        This method is called when the "Filter Models" button is clicked.
        """
        filter_value = self.int_filter_model.get_value_as_string().strip()
        
        if not filter_value:
            print("No filter value specified")
            return
            
        print(f"Applying filter for release: {filter_value}")
        self.apply_filter = True
        self.show_labels = True
        self.scroll_frame.rebuild()  # Update ScrollingFrame content with filter
        
    def _clear_filter(self):
        """
        Remove filter and show all SKU results.
        
        Resets the filter flag and triggers a rebuild of the scrolling frame
        to display all available SKUs without filtering.
        """
        self.apply_filter = False
        print("Filter cleared - showing all results")
        if self.show_labels:
            self.scroll_frame.rebuild()  # Update ScrollingFrame content without filter
        
    def _create_hierarchy_and_import_payload(self):
        """
        Create USD hierarchy and import payloads for selected SKUs.
        
        This is the main batch import function that:
        1. Gets the current USD stage context
        2. Retrieves the model name from UI
        3. Gets all selected SKUs from checkboxes
        4. For each selected SKU:
            - Creates the standardized USD hierarchy
            - Constructs the payload file path
            - Imports the USD payload
        
        The function integrates with the usd_tools module to perform
        the actual USD operations and uses the configuration paths
        to locate payload files.
        
        Example workflow:
            User selects model and SKUs ["001", "002"]
            -> Creates /World/Models/glass_Xform/Model_Xform/Release_v1.0/Model_001
            -> Creates /World/Models/glass_Xform/Model_Xform/Release_v1.0/Model_002
            -> Imports payloads from Model_001.usd and Model_002.usd
        """
        context = omni.usd.get_context()
        stage = context.get_stage()
        
        model_value = self.model_model.get_value_as_string()
        print(model_value)
        
        # Get selected SKUs from checkboxes
        get_selected = self._get_selected_items()
        
        # Process each selected SKU
        for data in get_selected:
            sku = data[0]
            release = data[1]
            
            # Create USD hierarchy structure
            usd_tools.create_hierarchy_structure(stage, model_value, sku, release)
            
            # Construct paths for payload import
            sku_prim_path = f"/World/Models/glass_Xform/{model_value}_Xform/Release_{release}/{model_value}_{sku}"
            main_usd_dir = config["paths"]["usd_dir"]["main"]
            payload_file_path = f"{main_usd_dir}\\{model_value}\\sku\\{model_value}_{sku}.usd"
            
            print(f" --> {payload_file_path}")
            print(f" --> {sku_prim_path}")
            
            # Import the payload
            usd_tools.import_payload(payload_file_path, sku_prim_path)
        
    def _get_selected_items(self):
        """
        Extract selected items from checkbox data.
        
        Iterates through all stored checkbox references and returns
        the SKU and release data for items that are currently checked.
        
        Returns:
            list: List of tuples containing (SKU, Release) for selected items
                
        Example:
            >>> selected = self._get_selected_items()
            >>> print(selected)
            [('001', '261'), ('003', '262')]
        """
        selected_items = [
            (data['sku'], data['release']) 
            for data in self.checkbox_data 
            if data['checkbox'].model.get_value_as_bool()
        ]
        
        print(f"Selected items: {selected_items}")
        return selected_items
        
    def _clear_all(self):
        """Clear both the scroll frame and any applied filters."""
        self.apply_filter = False
        self.show_labels = False
        self.checkbox_data = []
        self.scroll_frame.clear()
        print("Cleared all data and filters")
            
    def on_startup(self, _ext_id: str) -> ui.Window:
        """
        Extension startup method called when the extension is enabled.
        
        This method is automatically called by the Omniverse extension system
        when the extension is loaded. It:
        1. Creates the main window with specified dimensions
        2. Docks the window to the "Layers" panel
        3. Sets the window position and applies styling
        4. Builds the complete UI hierarchy including:
            - Dropdown selection frame
            - Custom model import interface
            - Optional USD path configuration
            - Image options panel
        
        Args:
            _ext_id (str): Extension identifier provided by the system
            
        Returns:
            ui.Window: Reference to the created main window
        """
        # Window configuration
        self.width = 450
        self.height = 600
        
        # Create main window
        self._editor_window = ui.Window("Thelios USD Tools", width=self.width, height=self.height)
        self._editor_window.deferred_dock_in("Layers")
        self._editor_window.setPosition(450, 100)
        self._editor_window.frame.set_style(DARK_WINDOW_STYLE)
        
        # Build window content
        with self._editor_window.frame:
            with ui.VStack():
                self._window_Frame = ui.ScrollingFrame(
                    name="canvas",
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                )
                with self._window_Frame:
                    with ui.VStack(height=0, name="main_v_stack", spacing=8):
                        
                        self._dropdown_import_template_UI()
                        
                        # Template scene import frame
                        self._dropdown_import_custom_template_scene_UI()
                        
                        # SKU-Release table creation
                        self._dropdown_custom_model_UI()
                        
                        # Main dropdown selection frame
                        self._dropdown_all_collection_UI()
                        
                        self._dropdown_render_UI()
                        
                        # Optional USD selection folder frame
                        with ui.CollapsableFrame(title="Optional USD Selection Folder ", 
                                                style=CollapsableFrame_style, collapsed=True):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                ui.Spacer(height=0)
                                self._create_path_combo("UI Path", "omni:/Project/Cool_ui.usd")
                                
                        # Image options frame
                        with ui.CollapsableFrame(title="Images Options", collapsed=True, 
                                                style=CollapsableFrame_style):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                self._create_path_combo("Images Path", "omni:/Library/Images/")
        
        return self._editor_window
        
    def on_shutdown(self):
        """
        Extension shutdown method called when the extension is disabled.
        
        This method is automatically called by the Omniverse extension system
        when the extension is unloaded. It performs cleanup by releasing
        the reference to the main window, allowing for proper garbage collection.
        
        Following the standard Omniverse extension pattern, this ensures
        clean shutdown and prevents memory leaks.
        """
        self._editor_window = None
