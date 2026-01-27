from posixpath import dirname
import omni.ui as ui
from omni.ui import color as cl
import omni.usd
from omni.kit.notification_manager import post_notification, NotificationStatus
from omni.kit.window.filepicker import FilePickerDialog
from omni.kit.widget.filebrowser import FileBrowserItem
import asyncio
import os
import shutil

from dataclasses import dataclass

from . import constants
from .models import TheliosWindowModel

from .tools.utils import queries as qu #plm_query, brand_query
from .tools.utils import usd_tools, template_tools, alerts
from .tools.render.custom_render_sequence import OmniCustomSequenceRenderer
from .tools.render import render_settings

@dataclass
class OnImportContext:
    _camera_checkbox: bool
    _lights_checkbox: bool
    #_limbo_checkbox: bool
    _settings_checkbox: bool
    _brand_camera_combo: str
    
class TheliosLogic:
    def __init__(self, model: TheliosWindowModel):
        
        self.model = model
        
        self.apply_filter = False
        self.show_labels = False 
        self.checkbox_data = []
        self.checkbox_render_data = []
        
        self.brand_combo = None
        self.type_combo = None
        self.release_field = None
        self.export_path_field = None
        
        self.start_slider = None
        self.current_payloads = []
        #self.resolution_combo = None
        
        self.templates_dir = constants.TEMPLATES_PATH
        
        self._stage = omni.usd.get_context().get_stage()
        
        self.alert_instance = alerts.AlertWindow()
        
        self._tree = constants.MAT_DICT
        
    # File Dialogs ------------------------------------------------------------------------------------
        
    def on_folder_icon_click(self, field):
        # Apertura FilePicker solo per cartelle
        
        def on_folder_selected(dialog, in_field, dirname):
                # Solo cartella selezionata
                dialog.hide()
                field.set_value(dirname)
        
        dialog = FilePickerDialog(
            "Select Folder",
            apply_button_label="Select",
            click_apply_handler=lambda field, dirname: on_folder_selected(dialog, field, dirname),
            select_folder=False  # Opzione solo cartella!
        )
        dialog.show()
        
    def on_folder_icon_click_file(self, field):
        # Apertura FilePicker solo per cartelle
        
        text_extensions = constants.TEXTURE_EXTENSIONS
        
        dialog = FilePickerDialog(
            "Select File",
            apply_button_label="Select",
            click_apply_handler=lambda filename, dirname: self.on_click_open(dialog, filename, dirname, field),
            item_filter_options=text_extensions,
            item_filter_fn=lambda item: self.on_filter_item(dialog, item),
            options_pane_build_fn=self.options_pane_build_fn
        )
        
    def on_click_open(self, dialog: FilePickerDialog, filename: str, dirname: str, field: ui.StringField):
        
        dirname = dirname.strip()
        if dirname and not dirname.endswith("/"):
            dirname += "/"
        fullpath = f"{dirname}{filename}"
        print(f"Opened file '{fullpath}'.")   
        
        dialog.hide()
        field.set_value(fullpath)
        
    def on_filter_item(self, dialog: FilePickerDialog, item: FileBrowserItem) -> bool:
        if not item or item.is_folder:
            return True
        if dialog.current_filter_option == 0:
            # Show only files with listed extensions
            _, ext = os.path.splitext(item.path)
            if ext in [".usd", ".usda", ".usdc", ".usdz"]:
                return True
            else:
                return False
        else:
            # Show All Files (*)
            return True 
        
    def options_pane_build_fn(self, selected_items):
        with ui.CollapsableFrame("Reference Options"):
            with ui.HStack(height=0, spacing=2):
                ui.Label("Prim Path", width=0)
        return True
        
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
        
    def get_combo_elements(self):
        combo_elements = qu.pop_combo_brands(constants.DB_KEY)
        return combo_elements
    
    def get_brand_from_code(self, code):
        key = code[:2]
        brand = constants.BRANDS_DICT.get(key)
        if brand:
            return brand.replace(" ", "_")
        return None
        
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
            if model_value == "":
                self.alert_instance.post_notification_info("Please enter a model name")
                return
            else:
                self.model_sku_res = qu.get_sku_model_plm(constants.DB_KEY, str(model_value))
                return self.model_sku_res
        
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
            
    # Payloads selection functions ---------------------------------------------------------------------
    
    def create_scrolling_frame_custom_model(self):
        self.scroll_frame_custom_model = ui.ScrollingFrame(
                        height=200,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
        return self.scroll_frame_custom_model
    
    def _import_sel_skus_custom_model(self):
            """
            Trigger the display of SKU selection interface.
            
            Sets the flag to show the SKU table labels and triggers a rebuild
            of the scrolling frame to display the available SKUs for selection.
            This method is called when the "Select Model" button is clicked.
            """
            #self.scroll_frame = self.create_scrolling_frame()
            self.show_labels = True
            self.scroll_frame_custom_model.rebuild()  # Update ScrollingFrame content
        
    def _get_selected_items_payloads(self):
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
        
    def _build_scrolling_content_custom_model(self):
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
        
        if sku_rel_list == []:
            self.alert_instance.post_notification_warning("No SKUs found for the specified model")
            return
        else:
        
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
        get_selected = self._get_selected_items_payloads()
        
        # Process each selected SKU
        for data in get_selected:
            sku = data[0]
            release = data[1]
            
            # Create USD hierarchy structure
            usd_tools.create_hierarchy_structure(self._stage, model_value, sku, release)
            
            # Construct paths for payload import
            sku_prim_path = f"/World/Models/glass_Xform/{model_value}_Xform/Release_{release}/{model_value}_{sku}"
            main_usd_dir = constants.BLOB_USD_PATH
            brand_name = self.get_brand_from_code(model_value)
            payload_file_path = f"{main_usd_dir}\\{brand_name}\\01_Models\\{model_value}\\sku\\{model_value}_{sku}.usd"
            
            print(f" --> {payload_file_path}")
            print(f" --> {sku_prim_path}")
            
            # Import the payload
            usd_tools.import_payload(payload_file_path, sku_prim_path)
            
        self.alert_instance.post_notification_info("Payloads imported successfully")
    
    # Rendering section --------------------------------------------------------------------------------
    
    def create_scrolling_frame_render(self):
        self.scroll_frame_render = ui.ScrollingFrame(
                        height=200,
                        horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                        vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    )
        return self.scroll_frame_render
    
    def _render_sequence(self, res_combo, model_name):
        
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
        
        renderer = OmniCustomSequenceRenderer(model_name,
                                                res_value, 
                                                export_path, 
                                                bool_value, 
                                                start_frame, 
                                                end_frame, 
                                                single_frame)
        
        asyncio.ensure_future(renderer.render_sequence())
        
    def _render_sequence_v2(self, res_combo, model_name):
        export_path = self.model.type_string_model.get_value_as_string()
        
        start_frame = self.model.startfr_model.get_value_as_int()
        end_frame = self.model.endfr_model.get_value_as_int()
        
        single_frame = self.model.singlefr_model.get_value_as_int()
        
        resolution_model = res_combo.get_item_value_model()
        
        seq_value = self.model.sequence_model.get_value_as_bool()
        single_value = self.model.single_model.get_value_as_bool()
        
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
        
        renderer = OmniCustomSequenceRenderer(model_name,
                                                res_value, 
                                                export_path, 
                                                bool_value, 
                                                start_frame, 
                                                end_frame, 
                                                single_frame)
        
        renderer.start_capture_extension_render()
        #asyncio.ensure_future(renderer.start_capture_extension_render())
        
    def _render_selected_skus(self, res_combo):
        get_selected_render = self._get_selected_items_render()
        
        for model in get_selected_render:
            # select the payload model
            self._get_selected_scope_string(model)
            #self._render_sequence_v2(res_combo, model)
            self._render_sequence(res_combo, model)
            
        #avviare il movie capture
        #esportare un file json nella cartella di destinazione con la lista dei modelli da renderizzare
        
        #--> quando ha finito di renderizzare un modello, lo toglie dalla lista
        
    async def _render_queue(self, res_combo, selected_skus):
        
        export_path = self.model.type_string_model.get_value_as_string()
        start_frame = self.model.startfr_model.get_value_as_int()
        end_frame = self.model.endfr_model.get_value_as_int()
        single_frame = self.model.singlefr_model.get_value_as_int()
        resolution_model = res_combo.get_item_value_model()
        seq_value = self.model.sequence_model.get_value_as_bool()
        single_value = self.model.single_model.get_value_as_bool()
        
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
            
        try:
            for model in selected_skus:
                
                self._get_selected_scope_string(model)
                
                print(f"Start render per modello {model}")
                renderer = OmniCustomSequenceRenderer(model,
                                                    res_value, 
                                                    export_path, 
                                                    bool_value, 
                                                    start_frame, 
                                                    end_frame, 
                                                    single_frame)
                
                await renderer.start_capture_extension_render_async()
                print(f"Finito render per modello {model}")
                
        except Exception as e:
            print(f"Errore nel render della coda: {e}")
            raise
            
    def _render_selected_skus_async(self, res_combo):
        payload_list = usd_tools.get_filtered_scopes()
        
        if payload_list == []:
            self.alert_instance.post_notification_warning("No SKUs selected for rendering")
            return
        else:
            if self.model.type_string_model.get_value_as_string() == "":
                self.alert_instance.post_notification_warning("Please specify an export path")
                return
            else:
                def ok_btn():
                    selected_skus = self._get_selected_items_render()
                    print(f"--- SKUs to render: {selected_skus} ---")
                    asyncio.ensure_future(self._render_queue(res_combo, selected_skus))
                    
                message = "Have you launched a small render queue before?\n "
                self.alert_instance.create_and_show_modal_window(message, ok_btn)
        
    def _get_selected_items_render(self):
        """
        Extract selected items from checkbox data.
        
        Iterates through all stored checkbox references and returns
        the SKU and release data for items that are currently checked.
        
        Returns:
            list: List of tuples containing (SKU, Release) for selected items
                
        Example:
            >>> selected = self._get_selected_items_payloads()
            >>> print(selected)
            [('001', '261'), ('003', '262')]
        """
        selected_items = [
            f"{data['model']}_{data['sku']}" 
            for data in self.checkbox_render_data 
            if data['checkbox'].model.get_value_as_bool()
        ]
        
        print(f"Selected items: {selected_items}")
        return selected_items
        
    def _build_scrolling_content_render(self):
        self.checkbox_render_data = []
        
        payload_list = usd_tools.get_filtered_scopes()
        
        with ui.VStack(spacing=0):
                for item in payload_list:
                    model = item.split("_")[0]
                    sku = item.split("_")[1]
                    
                    with ui.HStack():
                        # Style name in green
                        model_label = ui.Label(model,
                                                height=16, 
                                                style={"font_size":14, "color":cl("#28bfe9")}, 
                                                alignment=ui.Alignment.CENTER)
                        # SKU identifier
                        sku_label = ui.Label(sku, 
                                            height=16, 
                                            style={"font_size":16}, 
                                            alignment=ui.Alignment.CENTER)
                        
                        ui.Spacer()
                        # Selection checkbox
                        checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#28bfe9"), "background_color": cl(0.35)})
                        
                        # Store checkbox reference and associated data
                        self.checkbox_render_data.append({
                            'checkbox': checkbox,
                            'model': model,
                            'sku': sku
                        })    
        
    def _select_all_render_items(self):
        """
        Seleziona tutti i checkbox nella lista render.
        
        Itera attraverso tutti i checkbox memorizzati in checkbox_render_data
        e imposta il loro valore su True.
        """
        for data in self.checkbox_render_data:
            data['checkbox'].model.set_value(True)
        
        print(f"Selezionati {len(self.checkbox_render_data)} items")
        
    def _deselect_all_render_items(self):
        
        #Deseleziona tutti i checkbox nella lista render.
        
        for data in self.checkbox_render_data:
            data['checkbox'].model.set_value(False)
        
        print("Tutti gli items deselezionati")
        
    def _toggle_all_render_items(self):
        """
        Inverte lo stato di tutti i checkbox.
        Utile per un comportamento toggle del pulsante Select All.
        """
        # Verifica se almeno un item è selezionato
        any_selected = any(
            data['checkbox'].model.get_value_as_bool() 
            for data in self.checkbox_render_data
        )
        
        # Se qualcuno è selezionato, deseleziona tutto, altrimenti seleziona tutto
        if any_selected:
            self._deselect_all_render_items()
        else:
            self._select_all_render_items()  
        
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
        self.scroll_frame_custom_model.rebuild()  # Update ScrollingFrame content with filter
        
    def _clear_filter(self):
        """
        Remove filter and show all SKU results.
        
        Resets the filter flag and triggers a rebuild of the scrolling frame
        to display all available SKUs without filtering.
        """
        self.apply_filter = False
        print("Filter cleared - showing all results")
        if self.show_labels:
            self.scroll_frame_custom_model.rebuild()  # Update ScrollingFrame content without filter
            
    def _clear_all(self):
        """Clear both the scroll frame and any applied filters."""
        self.apply_filter = False
        self.show_labels = False
        self.checkbox_data = []
        self.checkbox_render_data = []
        self.scroll_frame_custom_model.clear()
        
        print("Cleared all data and filters")
            
    # Single template import functions ------------------------------------------------------------------
        
    def import_camera(self, brand_camera_combo):
        print("--- Import: Camera ---")
        self.combo_elements = self.get_combo_elements()
        self.brand_camera_model = brand_camera_combo.get_item_value_model()
        template_tools._import_camera(  self._stage, 
                                        self.brand_camera_model, 
                                        self.combo_elements)
        
    def import_lights(self):
        print("--- Import: Lights ---")
        template_tools._import_lights(self._stage)
        
    def import_limbo(self):
        pass
        #print("--- Import: Limbo ---")
        #template_tools._import_limbo(self._stage)
        
    def import_settings(self):
        print("--- Import: Settings ---")
        render_settings.import_render_settings()
        
    def on_import_click(self, context: OnImportContext):
                
        if context._camera_checkbox.model.get_value_as_bool():
            self.import_camera(context._brand_camera_combo)
            self.alert_instance.post_notification_info("Camera imported successfully!")
            
        if context._lights_checkbox.model.get_value_as_bool():
            self.import_lights()
            self.alert_instance.post_notification_info("Lights imported successfully!")
        """    
        if context._limbo_checkbox.model.get_value_as_bool():
            self.import_limbo()
            self.alert_instance.post_notification_info("Limbo imported successfully!")
        """    
        if context._settings_checkbox.model.get_value_as_bool():
            self.import_settings()
            self.alert_instance.post_notification_info("Settings imported successfully!")
            
        if not any([
            context._camera_checkbox.model.get_value_as_bool(),
            context._lights_checkbox.model.get_value_as_bool(),
            context._limbo_checkbox.model.get_value_as_bool(),
            context._settings_checkbox.model.get_value_as_bool()
        ]):
            
            self.alert_instance.post_notification_warning("No checkbox selected!")
            
        #Uncheck values
            
        context._camera_checkbox.model.set_value(False),
        context._lights_checkbox.model.set_value(False),
        context._limbo_checkbox.model.set_value(False),
        context._settings_checkbox.model.set_value(False)
            
    def on_import_click_all(self, context: OnImportContext):
                
        print("--- Import: All ---")
        
        self.import_camera(context._brand_camera_combo)
        self.import_lights()
        self.import_limbo()
        self.import_settings()
        
        context._camera_checkbox.model.set_value(False),
        context._lights_checkbox.model.set_value(False),
        #context._limbo_checkbox.model.set_value(False),
        context._settings_checkbox.model.set_value(False)
        
        self.alert_instance.post_notification_info("Full template imported successfully!")
        
    # View functions -------------------------------------------------------------------------------------

    def clear_and_populate_combo(self, combobox_model):
        
        payload_list = usd_tools.get_filtered_scopes()
        
        for item in combobox_model.get_item_children():
            combobox_model.remove_item(item)
            
        for payload in payload_list:
            combobox_model.append_child_item(None, ui.SimpleStringModel(payload))
            
        if payload_list:
            combobox_model.get_item_value_model().set_value(0)
        else:
            combobox_model.get_item_value_model().set_value(-1)  # nessuna selezione
            
        self._get_payloads_lenght()
                    
    def _get_selected_scope(self, combobox_model):
        payload_list = usd_tools.get_filtered_scopes()
        
        combo_string = combobox_model.get_item_value_model()
        combo_string_index = combo_string.as_int
        combo_string_value = payload_list[combo_string_index]
        
        print(f" ----------- Selected scope: {combo_string_value}")
        
        scopes_to_keep = constants.SCOPES_TO_KEEP
        print(f"Selected scope: {combo_string}")
        usd_tools.hide_all_scopes_except(combo_string_value, scopes_to_keep)
        
    def _get_selected_scope_string(self, model_string):
        
        print(f" ----------- Selected scope: {model_string}")
        
        scopes_to_keep = constants.SCOPES_TO_KEEP
        usd_tools.hide_all_scopes_except(model_string, scopes_to_keep)
        
    def _build_view_slider(self):
        payload_list = usd_tools.get_filtered_scopes()
        len_payloads = len(payload_list)
        self.start_slider = ui.IntSlider(value=1,min=1, max=len_payloads, step=1, style={"margin":3}).model
        return self.start_slider
    
    def _on_slider_changed(self, value):
        print(f"Slider value: {value}")
        payload_list = usd_tools.get_filtered_scopes()
        
        current_model_selected = payload_list[value.as_int - 1]
        self._get_selected_scope_string(current_model_selected)
        
        self.model.slider_view_model.set_value(str(current_model_selected))
            
    def _get_payloads_lenght(self):
        payload_list = usd_tools.get_filtered_scopes()
        return len(payload_list)
        
        #need some fixes here
        
    # Materials functions ---------------------------------------------------------------------------------
    
    def _fill_combo(self, model, items: list[str]):
        # Svuota
        for item in list(model.get_item_children()):
            model.remove_item(item)
        # Riempi
        for value in items:
            model.append_child_item(None, ui.SimpleStringModel(value))
        # Se c'è almeno un elemento, seleziona il primo
        if items:
            model.get_item_value_model().set_value(0)
            
    def _get_selected_text(self, model) -> str | None:
        children = model.get_item_children()
        if not children:
            return None
        idx = model.get_item_value_model().as_int
        if idx < 0 or idx >= len(children):
            return None
        return model.get_item_value_model(children[idx]).as_string
    
    def create_fld_mat(self, cat, subcat, code, name) -> str:
        print(f"{cat} - {subcat} - {code} - {name}")
        
        mat_name = f"{code}_{name}"
        dest_folder = constants.MAT_LIBRARY_PATH + f"\\{cat}\\{subcat}\\{mat_name}"
        
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
            print(f"Folder '{dest_folder}' created.")
            
        return dest_folder
            
    def copy_mat_to_dest_fld (self, dest_fld, category, new_name):
        
        master_mat_dict = constants.MAT_MASTER_DICT
        instance_material = master_mat_dict[category]
        print(f"Instance material: {instance_material}")
        
        master_mat_fld = constants.MASTER_MATERIAL_FLD
        
        final_source_fld = f"{master_mat_fld}\\{instance_material}"
        final_dest_fld = f"{dest_fld}\\{instance_material}"
        
        print(f" +++ Source folder: {final_source_fld}")
        print(f" *** Destination folder: {final_dest_fld}")
        
        if os.path.exists(dest_fld):
            shutil.copy(final_source_fld, final_dest_fld)
            print(f"Material copied to '{final_dest_fld}' successfully.")
            
            os.rename(final_dest_fld, f"{dest_fld}\\{new_name}.usda")
            print(f"Material renamed to '{new_name}.usda' successfully.")
            