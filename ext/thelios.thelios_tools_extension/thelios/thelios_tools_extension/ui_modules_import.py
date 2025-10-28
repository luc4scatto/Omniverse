import omni.ui as ui
from omni.ui import color as cl
import omni.usd

from .tools.templates import template_tools
from . import constants
from .models import TheliosWindowModel
from .logic import TheliosLogic

class ImportTemplateUI:
    def __init__(self):
        self._stage = omni.usd.get_context().get_stage()
        self._template_tools = template_tools
        
    def build(self, style):
        with ui.CollapsableFrame(title="Import Template Scene", style=style):
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
                
class CustomModelImportPanel:
    def __init__(self, model: TheliosWindowModel, logic: TheliosLogic):
        self.model = model
        self.logic = logic
        
    def build(self, style):
        with ui.CollapsableFrame(title="Custom Model Import ", style=style, collapsed=True):
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