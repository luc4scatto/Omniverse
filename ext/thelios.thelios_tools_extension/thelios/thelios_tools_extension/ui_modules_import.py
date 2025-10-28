import omni.ui as ui
from omni.ui import color as cl
import omni.usd
from omni.kit.notification_manager import post_notification, NotificationStatus
from omni.kit.window.filepicker import FilePickerDialog

from .tools.templates import template_tools
from . import constants
from .models import TheliosWindowModel
from .logic import TheliosLogic

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
                        
                    def on_import_click():
                        self.logic.on_import_click(camera_checkbox, 
                                                    lights_checkbox, 
                                                    limbo_checkbox, 
                                                    settings_checkbox, 
                                                    self.brand_camera_combo)
                        
                    def on_import_click_all():  
                        self.logic.on_import_click_all(camera_checkbox, 
                                                        lights_checkbox, 
                                                        limbo_checkbox, 
                                                        settings_checkbox, 
                                                        self.brand_camera_combo)
                    
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
                    self.import_custom_button = ui.Button("Select Model", clicked_fn=self.logic._import_sel_skus, name="select_model")
                    
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
                    
                    self.scroll_frame = self.logic.create_scrolling_frame()
                    
                    # Set build function for dynamic content
                    self.scroll_frame.set_build_fn(self.logic._build_scrolling_content)
                    
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
                    
    def _import_sel_skus(self):
            """
            Trigger the display of SKU selection interface.
            
            Sets the flag to show the SKU table labels and triggers a rebuild
            of the scrolling frame to display the available SKUs for selection.
            This method is called when the "Select Model" button is clicked.
            """
            self.show_labels = True
            self.scroll_frame.rebuild()  # Update ScrollingFrame content
            
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
        
        with ui.CollapsableFrame(title="Render", style=style, collapsed=False):
            with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                
                with ui.HStack(spacing=10):
                    
                    ui.Label("Exp. Path", name="label", width=constants.LABEL_PADDING)
                    
                    export_path_field = ui.StringField(self.model.type_string_model, name="export_path", height=10)
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
                    
                self.render_btn = ui.Button("Render", clicked_fn=self.logic._render_sequence, name="render_sequence")