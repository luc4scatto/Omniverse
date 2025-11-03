import omni.ui as ui
from omni.ui import color as cl
import omni.usd
from omni.kit.notification_manager import post_notification, NotificationStatus
import asyncio

from . import constants
from .models import TheliosWindowModel

from .tools.utils import queries as qu #plm_query, brand_query
from .tools.utils import usd_tools
from .tools.utils import template_tools
from .tools.render.custom_render_sequence import OmniCustomSequenceRenderer
from .tools.render import render_settings

class TheliosLogic:
    def __init__(self, model: TheliosWindowModel):
        
        self.model = model
        
        self.apply_filter = False
        self.show_labels = False 
        self.checkbox_data = []
        
        self.brand_combo = None
        self.type_combo = None
        self.release_field = None
        #self.resolution_combo = None
        
        self.templates_dir = constants.TEMPLATES_PATH
        
        self._stage = omni.usd.get_context().get_stage()
                    
    def like_radio(self, model, first):
            """Turn on the model and turn off two checkboxes"""
            if model.get_value_as_bool():
                model.set_value(True)
                first.model.set_value(False)
                
    def on_checkbox_changed(self,checkbox_model, slider):
            slider.enabled = checkbox_model.get_value_as_bool()
            # Cambia lo stile in base allo stato
            if slider.enabled:
                slider.style = constants.SLIDER_ENABLED_STYLE
            else:
                slider.style = constants.SLIDER_DISABLED_STYLE
                
    def _render_sequence(self, res_combo):
        
        export_path = self.model.type_string_model.get_value_as_string()
        
        start_frame = self.model.startfr_model.get_value_as_int()
        end_frame = self.model.endfr_model.get_value_as_int()
        
        single_frame = self.model.singlefr_model.get_value_as_int()
        
        resolution_model = res_combo.get_item_value_model()
        
        seq_value = self.model.sequence_model.get_value_as_bool()
        single_value = self.model.single_model.get_value_as_bool()
        
        #print(f"--- Sequence Value: {seq_value} ---")
        #print(f"--- Single Value: {single_value} ---")
        
        print(f"--- Export Path: {export_path} ---")
        
        if seq_value:
            bool_value = True
            print(f"--- Start Frame: {start_frame} ---")        
            print(f"--- End Frame: {end_frame} ---")
        elif single_value:
            bool_value = False
            print(f"--- Single Frame: {single_frame} ---")
        else:
            print("No render type selected, defaulting to Sequence")
            return
                
        res_index = resolution_model.as_int
        res_value = constants.RESOLUTIONS[res_index]
        
        print(f"--- Resolution: {res_value} ---")
        
        renderer = OmniCustomSequenceRenderer(constants.TEMP_NAME,
                                                res_value, 
                                                export_path, 
                                                bool_value, 
                                                start_frame, 
                                                end_frame, 
                                                single_frame)
        
        asyncio.ensure_future(renderer.render_sequence())
        
    def get_combo_elements(self):
        combo_elements = qu.pop_combo_brands(constants.DB_KEY)
        return combo_elements
        
    def create_scrolling_frame(self):
        self.scroll_frame = ui.ScrollingFrame(
                        height=200,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
        return self.scroll_frame
        
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
        
        model_value = self.model.model_model.get_value_as_string()
        print(model_value)
        
        # Get selected SKUs from checkboxes
        get_selected = self._get_selected_items()
        
        # Process each selected SKU
        for data in get_selected:
            sku = data[0]
            release = data[1]
            
            # Create USD hierarchy structure
            usd_tools.create_hierarchy_structure(self._stage, model_value, sku, release)
            
            # Construct paths for payload import
            sku_prim_path = f"/World/Models/glass_Xform/{model_value}_Xform/Release_{release}/{model_value}_{sku}"
            main_usd_dir = constants.BLOB_PATH
            payload_file_path = f"{main_usd_dir}\\{model_value}\\sku\\{model_value}_{sku}.usd"
            
            print(f" --> {payload_file_path}")
            print(f" --> {sku_prim_path}")
            
            # Import the payload
            usd_tools.import_payload(payload_file_path, sku_prim_path)
            
    # PLM query functions -------------------------------------------------------------------------------
        
    def _get_sku_model_plm(self):
            """
            Retrieve SKU and model data from PLM for the specified model.
            
            Queries the PLM system for all SKUs associated with the currently
            entered model name. Used to populate the SKU selection table.
            
            Returns:
                list: List of tuples containing (SKU, Release, Style) data
                        for the specified model
            """
            model_value = self.model.model_model.get_value_as_string()
            model_sku_res = qu.get_sku_model_plm(constants.DB_KEY, str(model_value))
            return model_sku_res
        
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
        combo_elements = self.get_combo_elements()
        
        # Extract current selections from UI
        brand_model = self.brand_combo.get_item_value_model()
        brand_index = brand_model.as_int
        brand_value = combo_elements[brand_index]
        
        type_model = self.type_combo.get_item_value_model()
        type_index = type_model.as_int
        type_value = constants.GENRES[type_index]
        
        season_value = self.model.int_model.get_value_as_int()
        
        print(f"+++ Season: {season_value}")
        print(f"--- Brand: {brand_value}")
        print(f"*** Type: {type_value}")
        
        # Handle combined queries for "All Woman" category
        if type_value == "All Woman":
            res_query_optical_woman = qu.get_plm_data(constants.DB_KEY,str(season_value),str(brand_value),"Optical - Woman")
            res_query_sun_woman = qu.get_plm_data(constants.DB_KEY,str(season_value),str(brand_value),"Sun - Woman")
            
            res_query_sun = list(set(res_query_optical_woman).union(set(res_query_sun_woman)))
            sorted_list = sorted(res_query_sun, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        # Handle combined queries for "All Man" category
        elif type_value == "All Man":
            res_query_optical_man = qu.get_plm_data(constants.DB_KEY,str(season_value),str(brand_value),"Optical - Man")
            res_query_sun_man = qu.get_plm_data(constants.DB_KEY,str(season_value),str(brand_value),"Sun - Man")
            
            result_query_man = list(set(res_query_optical_man).union(set(res_query_sun_man)))
            sorted_list = sorted(result_query_man, key=lambda x: x[0])
            print(sorted_list)
            return sorted_list
            
        # Handle single category queries
        else:
            res_query = qu.get_plm_data(constants.DB_KEY,str(season_value),str(brand_value),str(type_value))
            print(res_query)
            return res_query
        
    # ---------------------------------------------------------------------------------------------------
    
    def _import_sel_skus(self):
            """
            Trigger the display of SKU selection interface.
            
            Sets the flag to show the SKU table labels and triggers a rebuild
            of the scrolling frame to display the available SKUs for selection.
            This method is called when the "Select Model" button is clicked.
            """
            #self.scroll_frame = self.create_scrolling_frame()
            self.show_labels = True
            self.scroll_frame.rebuild()  # Update ScrollingFrame content
        
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
            filter_value = self.model.int_filter_model.get_value_as_string().strip()
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
                        
    # Filtering an cleaning functions -------------------------------------------------------------------
        
    def _filter_skus(self):
        """
        Apply filter to SKU results based on release value.
        
        Sets the filter flag and triggers a rebuild of the scrolling frame
        to display only SKUs that match the filter criteria.
        This method is called when the "Filter Models" button is clicked.
        """
        filter_value = self.model.int_filter_model.get_value_as_string().strip()
        
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
            
    def _clear_all(self):
        """Clear both the scroll frame and any applied filters."""
        self.apply_filter = False
        self.show_labels = False
        self.checkbox_data = []
        self.scroll_frame.clear()
        print("Cleared all data and filters")
        
    def _clear_all(self):
        """Clear both the scroll frame and any applied filters."""
        self.apply_filter = False
        self.show_labels = False
        self.checkbox_data = []
        self.scroll_frame.clear()
        print("Cleared all data and filters")
        
    # ---------------------------------------------------------------------------------------------------
    
    # Single template import functions ------------------------------------------------------------------
        
    def import_camera(self, brand_camera_combo):
        print("--- Import: Camera ---")
        self.combo_elements = self.get_combo_elements()
        self.brand_camera_model = brand_camera_combo.get_item_value_model()
        template_tools._import_camera(  self._stage, 
                                        self.brand_camera_model, 
                                        self.combo_elements, 
                                        self.templates_dir)
        
    def import_lights(self):
        print("--- Import: Lights ---")
        template_tools._import_lights(self._stage, self.templates_dir)
        
    def import_limbo(self):
        print("--- Import: Limbo ---")
        template_tools._import_limbo(self._stage, self.templates_dir)
        
    def import_settings(self):
        print("--- Import: Settings ---")
        render_settings.import_render_settings()
        
    def on_import_click(self, 
                        camera_checkbox, 
                        lights_checkbox, 
                        limbo_checkbox, 
                        settings_checkbox,
                        brand_camera_combo):
                
        if camera_checkbox.model.get_value_as_bool():
            self.import_camera(brand_camera_combo)
            
        if lights_checkbox.model.get_value_as_bool():
            self.import_lights()
            
        if limbo_checkbox.model.get_value_as_bool():
            self.import_limbo()
            
        if settings_checkbox.model.get_value_as_bool():
            self.import_settings()
            
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
            
    def on_import_click_all(self,
                            camera_checkbox, 
                            lights_checkbox, 
                            limbo_checkbox, 
                            settings_checkbox,
                            brand_camera_combo):
                
        print("--- Import: All ---")
        
        self.import_camera(brand_camera_combo)
        self.import_lights()
        self.import_limbo()
        self.import_settings()
        
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