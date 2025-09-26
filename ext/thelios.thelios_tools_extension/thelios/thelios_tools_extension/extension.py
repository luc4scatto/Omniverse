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
import omni.usd
from omni.ui import color as cl
from pxr import Usd, UsdGeom, Sdf

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

# Setup module paths
query_dir = f"{ext_fld}/tools/queries"
style_dir = f"{ext_fld}/tools/style"
usd_dir = f"{ext_fld}/tools/usd"

add_fld = [query_dir, style_dir, usd_dir]

# Add custom module paths to sys.path
for fld in add_fld:
    if fld not in sys.path:
        sys.path.append(fld)
        
# Import custom modules
import brand_query, plm_query, style_widgets, usd_tools

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
        
        self._editor_window = None
        self._window_Frame = None
        
        # UI Data models
        self.int_model = ui.SimpleIntModel(262)
        self.model_model = ui.SimpleStringModel()
        self.brand_string_model = ui.SimpleStringModel()
        self.type_string_model = ui.SimpleStringModel()
        
        # State management
        self.show_labels = False
        self.checkbox_data = []
                
    def set_style_dark(self):
        """
        Apply dark theme styling to the main window frame.
        
        This method applies the predefined dark window style to the main
        window frame for consistent visual appearance.
        """
        self._window_Frame.set_style(DARK_WINDOW_STYLE)
        
    def _build_dropdown_frame_all_collection(self):
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
        with ui.Frame():
            with ui.ZStack():
                ui.Rectangle(name="frame_background")
                with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                    ui.Spacer(height=5)
                    
                    # Release input field
                    with ui.HStack(spacing=10):
                        ui.Label("Release", name="label", width=LABEL_PADDING)
                        self.release_field = ui.IntField(self.int_model, height=10, name="release")
                        self._create_control_state()
                        
                    # Brand selection dropdown
                    with ui.HStack(spacing=10):
                        ui.Label("Brand", name="label", width=LABEL_PADDING)
                        self.brand_combo = ui.ComboBox(1, *combo_elements, height=10, name="brand_choices").model
                        self._create_control_state()
                        
                    # Type/Genre selection dropdown
                    with ui.HStack(spacing=10):
                        ui.Label("Type", name="label", width=LABEL_PADDING)
                        self.type_combo = ui.ComboBox(0, *genres, height=10, name="type_choices").model
                        self._create_control_state()
                        
                    # Import button
                    self.import_btn = ui.Button("Import", clicked_fn=self._get_plm_data)
                    ui.Spacer(height=0)
                    
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
        Build the scrollable content for SKU selection table.
        
        Creates a dynamic table showing available SKUs for the selected model.
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
        
    def _import_custom_model(self):
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
        with ui.CollapsableFrame(title="Custom Model Import ", style=CollapsableFrame_style):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                # Model input and select button
                with ui.HStack(spacing=10):
                    ui.Label("Model", name="label", width=LABEL_PADDING)
                    self.model_field = ui.StringField(self.model_model, height=10, name="model")
                    self.import_custom_button = ui.Button("Select Model", height=10, clicked_fn=self._import_sel_skus)
                
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
                    
                    # Import button for selected SKUs
                    self.create_hierarchy_button = ui.Button("Import selected SKUs", 
                                                            height=10, 
                                                            clicked_fn=self._create_hierarchy_and_import_payload)
                    
                    ui.Spacer(height=8)
            
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
                        
                        # Main dropdown selection frame
                        self._build_dropdown_frame_all_collection()
                        
                        # SKU-Release table creation
                        self._import_custom_model()
                        
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
