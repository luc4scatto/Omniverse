import omni.ui as ui
import omni.ext
from omni.ui import color as cl
import omni.usd
from omni.kit.window.filepicker import FilePickerDialog

from omni.kit.widget.searchable_combobox import build_searchable_combo_widget, ComboBoxListDelegate

from pathlib import Path

from .tools.utils import template_tools
from . import constants
from .models import TheliosWindowModel
from .logic import TheliosLogic, OnImportContext
from .tools.style import style_widgets
from .tools.utils import usd_tools

class ImportTemplatePanel:
    def __init__(self):
        self._stage = omni.usd.get_context().get_stage()
        self._template_tools = template_tools
        
    def build(self, style):
        with ui.CollapsableFrame(title="Import Template Scene", style=style, collapsed=constants.IMPORT_TEMPLATE_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                def like_radio(model, first, second):
                    if model.get_value_as_bool():
                        model.set_value(True)
                        first.model.set_value(False)
                        second.model.set_value(False)
                        
                with ui.HStack(spacing=12):
                    self.abc_checkbox = ui.CheckBox(width=30, 
                                                    height=16, 
                                                    style={"color": "#77b901", "background_color": 0.35})
                    ui.Label("ABC", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": 0.3, "margin": 0})
                    
                    self.configurator_checkbox = ui.CheckBox(width=30, 
                                                            height=16, 
                                                            style={"color": "#77b901", "background_color": 0.35})
                    ui.Label("Configurator", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": 0.3, "margin": 0})
                    
                    self.site_checkbox = ui.CheckBox(width=30, 
                                                    height=16, 
                                                    style={"color": "#77b901", "background_color": 0.35})
                    ui.Label("Site", name="label")
                    
                    self.configurator_checkbox.model.add_value_changed_fn(lambda a, b=self.abc_checkbox, c=self.site_checkbox: like_radio(a, b, c))
                    self.abc_checkbox.model.add_value_changed_fn(lambda a, b=self.configurator_checkbox, c=self.site_checkbox: like_radio(a, b, c))
                    self.site_checkbox.model.add_value_changed_fn(lambda a, b=self.configurator_checkbox, c=self.abc_checkbox: like_radio(a, b, c))
                    
                    self.abc_checkbox.model.set_value(True)
                    
                def on_import_click():
                    if self.abc_checkbox.model.get_value_as_bool():
                        self._template_tools._import_camera(self._stage, "Brand")
                    elif self.configurator_checkbox.model.get_value_as_bool():
                        self._template_tools._import_lights(self._stage)
                    elif self.site_checkbox.model.get_value_as_bool():
                        self._template_tools._import_limbo(self._stage)
                        
                self.import_template_btn = ui.Button("Import Template", name="import_template", clicked_fn=on_import_click)
                
class CustomTemplateImportPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
        self._stage = omni.usd.get_context().get_stage()
        self._template_tools = template_tools
        
        self.combo_elements = self.logic.get_combo_elements()
        
    def build(self, style):
        with ui.CollapsableFrame(title="Custom Import Template Scene ", style=style, collapsed=constants.CUSTOM_IMPORT_TEMPLATE_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                    
                # Brand selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Camera Selection", name="label", width=constants.LABEL_PADDING)
                    self.brand_camera_combo = ui.ComboBox(1, *self.combo_elements, height=10, name="camera_brand").model
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
                    """
                    with ui.HStack():
                        limbo_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Limbo", name="label")
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0})    
                    """
                    with ui.HStack():
                        settings_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35)})
                        ui.Label("Settings", name="label")
                        
                    def on_import_click():
                        context = OnImportContext(_camera_checkbox = camera_checkbox, 
                                                    _lights_checkbox = lights_checkbox, 
                                                    #_limbo_checkbox = limbo_checkbox, 
                                                    _settings_checkbox = settings_checkbox,
                                                    _brand_camera_combo = self.brand_camera_combo)
                        self.logic.on_import_click(context)
                        
                    def on_import_click_all():  
                        context = OnImportContext(_camera_checkbox = camera_checkbox, 
                                                    _lights_checkbox = lights_checkbox, 
                                                    #_limbo_checkbox = limbo_checkbox, 
                                                    _settings_checkbox = settings_checkbox,
                                                    _brand_camera_combo = self.brand_camera_combo)
                        self.logic.on_import_click_all(context)
                    
                # Import button
                self.import_temp_item_btn = ui.Button("Import Selected", clicked_fn=on_import_click, name="import_collection")
                
                ui.Rectangle(height=1, style={"background_color": cl(0.3), "margin": 0})
                
                self.import_all_temp_item_btn = ui.Button("Import All", clicked_fn=on_import_click_all, name="import_collection")
                
class CustomModelImportPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
    def build(self, style):
        with ui.CollapsableFrame(title="Custom Model Import ", style=style, collapsed=constants.CUSTOM_MODEL_IMPORT_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=15, name="frame_v_stack"):
                # Model input and select button
                with ui.HStack(spacing=10, alignment=ui.Alignment.V_CENTER):
                    ui.Label("Model", name="label", width=constants.LABEL_PADDING)
                    self.model_field = ui.StringField(self.model.model_model, name="model", height=10, style={"margin":3})
                    self.import_custom_button = ui.Button("Select Model", clicked_fn=self.logic._import_sel_skus_custom_model, name="select_model")
                    
                with ui.ZStack():
                    ui.Rectangle(style={"background_color": cl(0.25), 
                                        "padding": 8, 
                                        "border_radius": 2, 
                                        "margin": -4} )  
                    
                    with ui.HStack(height=0, spacing=10, alignment=ui.Alignment.V_CENTER):
                        ui.Label("Rel Filter", name="label", width=constants.LABEL_PADDING)
                        self.season_field = ui.StringField(self.model.int_filter_model, name="filter", style={"margin":3})
                        self.filter_button = ui.Button("Filter", clicked_fn=self.logic._filter_skus)
                        self.clear_filter_button = ui.Button("Clear Filter", clicked_fn=self.logic._clear_filter, name="clear_filter", style= {})
                
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
                    
                    self.scroll_frame_custom_model = self.logic.create_scrolling_frame_custom_model()
                    
                    # Set build function for dynamic content
                    self.scroll_frame_custom_model.set_build_fn(self.logic._build_scrolling_content_custom_model)
                    
                    ui.Spacer(height=16)
                    with ui.HStack():
                        # Import button for selected SKUs
                        self.create_hierarchy_button = ui.Button("Import selected SKUs", 
                                                                height=10, 
                                                                clicked_fn=self.logic._create_hierarchy_and_import_payload,
                                                                name="import_selected")
                        
                        self.clear_button = ui.Button("Clear", 
                                                                height=10, 
                                                                clicked_fn=self.logic._clear_all,
                                                                name = "clear_scrolling")
                    
                    ui.Spacer(height=8)
            
class ImportAllCollectionPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        self.combo_elements = self.logic.get_combo_elements()
        
    def build(self, style):
        with ui.CollapsableFrame(title="All Collection Import ", style=style, collapsed=constants.IMPORT_ALL_COLLECTION_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                # Release input field
                with ui.HStack(spacing=10):
                    ui.Label("Release", name="label", width=constants.LABEL_PADDING)
                    self.release_field = ui.IntField(self.model.release_model, height=10, name="release")
                    #self._create_control_state()
                    
                # Brand selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Brand", name="label", width=constants.LABEL_PADDING)
                    self.brand_combo = ui.ComboBox(1, *self.combo_elements, height=10, name="brand_choices").model
                    #self._create_control_state()
                    
                # Type/Genre selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Type", name="label", width=constants.LABEL_PADDING)
                    self.type_combo = ui.ComboBox(0, *constants.GENRES, height=10, name="type_choices").model
                    #self._create_control_state()
                    
                # Import button
                self.import_btn = ui.Button("Import", clicked_fn=self.logic._get_plm_data, name="import_collection")
                ui.Spacer(height=0)
                
class RenderSettingsPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
    def build(self, style):
                
        def on_folder_selected(dialog, filename, dirname):
            # Solo cartella selezionata
            dialog.hide()
            self.export_path_field.model.set_value(dirname)
        
        def on_folder_icon_click():
            # Apertura FilePicker solo per cartelle
            dialog = FilePickerDialog(
                "Seleziona cartella di export",
                apply_button_label="Seleziona",
                click_apply_handler=lambda filename, dirname: on_folder_selected(dialog, filename, dirname),
                select_folder=True  # Opzione solo cartella!
            )
            dialog.show()
            
        with ui.CollapsableFrame(title="Render", style=style, collapsed=constants.RENDER_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                # Main container for the table
                with ui.VStack(spacing=0):
                    # Table headers
                    with ui.HStack():
                        ui.Label("MODEL", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        ui.Label("SKU", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        #ui.Label("RELEASE", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                        ui.Label("IMPORT", style={"font_weight": "bold", "font_size": 16}, alignment=ui.Alignment.CENTER)
                    
                    ui.Spacer(height=4)
                    
                    # ScrollingFrame with internal Frame for content
                    
                    self.scroll_frame_render = self.logic.create_scrolling_frame_render()
                    
                    # Set build function for dynamic content
                    def create_scrolling_content_render():
                        self.scroll_frame_render.set_build_fn(self.logic._build_scrolling_content_render)
                        
                    ui.Spacer(height=10)
                    
                    with ui.HStack(spacing=10):
                        self.refresh_render_select_btn = ui.Button("Refresh", clicked_fn= create_scrolling_content_render,name="render_sequence")
                        self.select_all_render_select_btn = ui.Button("Select All", clicked_fn=self.logic._select_all_render_items, name="render_sequence")
                        self.deselect_all_render_select_btn = ui.Button("Deselect All", clicked_fn=self.logic._deselect_all_render_items, name="render_sequence")
                        
                    #self.render_render_select_btn = ui.Button("Render Selected", clicked_fn= self.logic._render_selected_skus, name="render_sequence")
                    
                    #self.refresh_render_select_btn = ui.Button("Refresh", clicked_fn= self.logic._render_selected_skus,name="render_sequence")
                
                with ui.HStack(spacing=10):
                    
                    ui.Label("Exp. Path", name="label", width=constants.LABEL_PADDING)
                    
                    self.export_path_field = ui.StringField(self.model.type_string_model, name="export_path", height=10)
                    
                    ui.Button(name="Scegli cartella", 
                            image_url="resources/icons/folder.png", 
                            alignemnt=ui.Alignment.TOP,
                            width=28,
                            height=28,
                            clicked_fn=on_folder_icon_click,
                            style={"margin":3, "background_color": cl(0)})
                    #self._create_control_state()
                    
                with ui.HStack(spacing=10):
                    ui.Label("Resolution", name="label", width=constants.LABEL_PADDING)
                    self.resolution_combo = ui.ComboBox(0, *constants.RESOLUTIONS, height=10, name="type_choices").model
                    #self._create_control_state()
                    
                with ui.HStack():
                    
                    sequence_checkbox = ui.CheckBox(width=30, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35),"margin":6},
                                            model=self.model.sequence_model,
                                            name="sequence_checkbox")
                    ui.Label("Sequence", name="label")
                    
                    single_checkbox = ui.CheckBox(width=36, 
                                            height=16, 
                                            style={"color":cl("#77b901"), "background_color": cl(0.35),"margin":6},
                                            model=self.model.single_model,
                                            name="single_checkbox")
                    ui.Label("Single", name="label")
                    
                    sequence_checkbox.model.add_value_changed_fn(lambda a, b=single_checkbox: self.logic.like_radio(a, b))
                    single_checkbox.model.add_value_changed_fn(lambda a, b=sequence_checkbox: self.logic.like_radio(a, b))
                    
                ui.Rectangle(height=1, style={"background_color": cl(0.3), "margin": 0})
                
                with ui.HStack(spacing=10):
                    ui.Label("Start/End", name="label", width=constants.LABEL_PADDING)
                    self.start_slider = ui.IntSlider(min=1, max=8, step=1)
                    self.start_slider.model = self.model.startfr_model
                    self.start_slider.enabled = True # parte disattivato
                    
                    self.end_slider = ui.IntSlider(min=1, max=8 ,step=1)
                    self.end_slider.model = self.model.endfr_model
                    self.end_slider.enabled = True # parte disattivato
                    #self._create_control_state()
                    
                    ui.Rectangle(width=1, style={"background_color": cl(0.3), "margin": 0}) 
                    
                    ui.Label("Single Frame", name="label", width=constants.LABEL_PADDING)
                    self.single_slider = ui.IntSlider(min=1, max=8 ,step=1, style=constants.SLIDER_DISABLED_STYLE)
                    self.single_slider.model = self.model.singlefr_model
                    self.single_slider.enabled = False # parte disattivato
                    #self._create_control_state()
                    
                sequence_checkbox.model.add_value_changed_fn(lambda model: self.logic.on_checkbox_changed(model, self.start_slider))  
                sequence_checkbox.model.add_value_changed_fn(lambda model: self.logic.on_checkbox_changed(model, self.end_slider))  
                single_checkbox.model.add_value_changed_fn(lambda model: self.logic.on_checkbox_changed(model, self.single_slider))
                    
                #self.render_btn = ui.Button("Render", clicked_fn=lambda combobox = self.resolution_combo: self.logic._render_selected_skus(combobox), name="render_sequence")
                self.render_render_select_btn = ui.Button("Render Selected", clicked_fn= lambda combobox = self.resolution_combo: self.logic._render_selected_skus_async(combobox), name="render_sequence")

class ViewPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
        self.payloads_combo = None
        self.refresh_btn = None
        self.select_btn = None
        
        self.slider_container = None  # contenitore dinamico per slider, bottoni e stringfield
        self.current_slider_value = 1
        
    def build(self, style):
        with ui.CollapsableFrame(title="View", style=style, collapsed=constants.VIEW_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                with ui.HStack(spacing=5):
                    self.payloads_combo = ui.ComboBox(0, "", height=10, name="combo_payloads", style={"margin":3}).model
                    self.refresh_btn = ui.Button("Refresh", clicked_fn=self._refresh_ui, name="refresh_button")
                    self.select_btn = ui.Button("Select", clicked_fn=lambda combobox=self.payloads_combo: self.logic._get_selected_scope(combobox), name="select_button")
                
                #searchable_combo_box = self.create_searchable_combo_box()
                
                ui.Rectangle(height=1, style={"background_color": cl(0.3), "margin": 0})
                
                self.slider_container = ui.VStack()
        
    def _build_dynamic_slider_ui(self):
        
        string_style = style_widgets.string_field_style
        button_style = style_widgets.button_style
        
        self.slider_container.clear()
        
        # Riga con bottone indietro, slider, bottone avanti
        with self.slider_container:
            with ui.HStack(spacing=5):
                self.back_frame_btn = ui.Button(width=50, 
                                                name="back_fr_button",
                                                style=button_style, 
                                                clicked_fn=self._backward_frame,
                                                image_url=str(constants.BACK_FRAME_ICON))
                
                len_payloads = self.logic._get_payloads_lenght()
                self.start_slider_widget = ui.IntSlider(min=1, max=len_payloads, step=1,
                                                        value=self.current_slider_value, style={"margin":3})
                self.start_slider = self.start_slider_widget.model
                self.start_slider_sub = self.start_slider.subscribe_value_changed_fn(self._on_slider_changed)
                
                self.fwd_frame_btn = ui.Button(width=50, 
                                            name="fwd_fr_button", 
                                            style=button_style,
                                            clicked_fn=self._forward_frame,
                                            image_url=str(constants.FWD_FRAME_ICON))
                
            ui.Spacer(height=4)
            # Riga sotto SOLO per il StringField — sarà “a capo”, cioè su una riga tutta sua
            with ui.VStack():
                self.selected_model_field = ui.StringField(
                    self.model.slider_view_model, name="sel_model", style=string_style
            )
    
    def _forward_frame(self):
        payload_list = usd_tools.get_filtered_scopes()
        current_value = self.start_slider.get_value_as_int()
        new_value = current_value + 1
        max_val = len(payload_list)
        
        if new_value > max_val:
            new_value = max_val
            
        self.start_slider.set_value(new_value)
        self.current_slider_value = new_value
        
    def _backward_frame(self):
        current_value = self.start_slider.get_value_as_int()
        new_value = current_value - 1
        
        if new_value <= 1:
            new_value = 1
            
        self.start_slider.set_value(new_value)
        self.current_slider_value = new_value
    
    def _refresh_ui(self):
        self.logic.clear_and_populate_combo(self.payloads_combo)
        self._build_dynamic_slider_ui()
        
    def _on_slider_changed(self, value):
        v = value.as_int
        if v < 1:
            print(f"Warning: slider value < 1: {v}, clamping to 1")
            v = 1
        payload_list = usd_tools.get_filtered_scopes()
        current_model_selected = payload_list[v - 1]
        # Qui chiami la funzione dentro logic, non dentro ViewPanel
        self.logic._get_selected_scope_string(current_model_selected)
        self.model.slider_view_model.set_value(str(current_model_selected))
        
    def create_searchable_combo_box(self):
        # Define a callback function to be called when an item is selected
        def on_combo_click_fn(model):
            selected_item = model.get_value_as_string()
            print(f"Selected item: {selected_item}")
            
        # Define the list of items for the combo box
        
        if usd_tools.get_filtered_scopes() is None:
            item_list = ["-"]
        else:
            item_list = usd_tools.get_filtered_scopes()
            
        # Create the searchable combo box with the specified items and callback
        searchable_combo_widget = build_searchable_combo_widget(
            combo_list=item_list,
            combo_index=-1,  # Start with no item selected
            combo_click_fn=on_combo_click_fn,
            widget_height=18,
            default_value="Select an item",  # Placeholder text when no item is selected
            window_id="SearchableComboBoxWindow",
            delegate=ComboBoxListDelegate()  # Use the default delegate for item rendering
        )
        
        # Return the created widget
        return searchable_combo_widget
    
class MaterialsPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
        self._tree = constants.MAT_DICT
        
    def build(self, style):
        with ui.CollapsableFrame(title="Materials ", style=style, collapsed=constants.MATERIALS_UI_VISIBILITY):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                # Release input field
                with ui.HStack(spacing=10):
                    ui.Label("Category", name="label", width=constants.LABEL_PADDING)
                    self._cat_combo = ui.ComboBox(0, "", height=10, name="combo_cat", style={"margin":3}).model
                    ui.Label("Sub-Category", name="label", width=constants.LABEL_PADDING)
                    self.sub_cat_combo = ui.ComboBox(0, "", height=10, name="combo_sub_cat", style={"margin":3}).model
                    
                    self.logic._fill_combo(self._cat_combo, list(self._tree.keys()))
                    # Callback quando cambia la selezione del primo
                    self._cat_combo.add_item_changed_fn(self._on_macro_changed)
                    
                # Brand selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Code", name="label", width=constants.LABEL_PADDING)
                    self.model_field = ui.StringField(self.model.model_model, name="model", height=10, style={"margin":3})
                    
                    ui.Label("Name", name="label", width=constants.LABEL_PADDING)
                    self.model_field = ui.StringField(self.model.model_model, name="model", height=10, style={"margin":3})
                    #self._create_control_state()
                    
                # Type/Genre selection dropdown
                with ui.HStack(spacing=10):
                    ui.Label("Textures", name="label", width=constants.LABEL_PADDING)
                    
                    self.export_path_field = ui.StringField(self.model.type_string_model, name="export_path", height=10)
                    ui.Button(name="Scegli cartella", 
                            image_url="resources/icons/folder.png", 
                            alignemnt=ui.Alignment.TOP,
                            width=28,
                            height=28,
                            clicked_fn=lambda: print("Select folder clicked"),
                            style={"margin":3, "background_color": cl(0)})
                    
                # Create material buttton
                self.create_mtl_btn = ui.Button("Create Material", clicked_fn=self.logic._get_plm_data, name="import_collection")
                ui.Spacer(height=0)
                
    
    
    def _on_macro_changed(self, model, item):
        selected = self.logic._get_selected_text(model)
        if not selected:
            self.logic._fill_combo(self.sub_cat_combo, [])
            return
        
        sub_dict = self._tree.get(selected, {})
        # Chiavi del livello successivo
        sub_items = list(sub_dict.keys())
        self.logic._fill_combo(self.sub_cat_combo, sub_items)
        
        return sub_items