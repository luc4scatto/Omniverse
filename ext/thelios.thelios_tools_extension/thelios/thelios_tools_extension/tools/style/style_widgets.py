
import omni.ui as ui
from omni.ui import color as cl

def window_style():
    
    KIT_GREEN = 0xFF8A8777
    
    DARK_WINDOW_STYLE = {
        "Window": {"background_color": 0xFF444444},
        #-----------------------------------------------------------------------------------------------------
        "Button": {"background_color": 0xFF292929, 
                    "margin": 3, 
                    "padding": 3, 
                    "border_radius": 2,
                    "height": 10},
        
        "Button.Label": {"color": 0xFFCCCCCC},
        "Button:hovered": {"background_color": 0xFF9E9E9E},
        "Button:pressed": {"background_color": 0xC22A8778},
        
        #Clear buttons style
        "Button::clear_filter:hovered": {"background_color": cl("#a94545")},
        "Button::clear_scrolling:hovered": {"background_color": cl("#a94545")},
        
        "Button::select_model:hovered": {"background_color": cl("#77b901")},
        "Button::import_selected:hovered": {"background_color": cl("#77b901")},
        "Button::import_collection:hovered": {"background_color": cl("#77b901")},
        #-----------------------------------------------------------------------------------------------------
        "VStack::main_v_stack": {"secondary_color": 0x0, "margin_width": 0, "margin_height": 0},
        "VStack::frame_v_stack": {"margin_width": 8},
        #-----------------------------------------------------------------------------------------------------
        "Rectangle::frame_background": {"background_color": 0xFF343432, "border_radius": 5},
        "Rectangle::add": {"background_color": 0xFF23211F},
        "Rectangle:hovered:add": {"background_color": 0xFF73414F},
        "Triangle::title": {"background_color": 0xFFAAAAAA},
        "Circle::transform": {"background_color": 0x558A8777},
        #-----------------------------------------------------------------------------------------------------
        "Frame": {"background_color": 0xFFAAAAAA},
        
        "CollapsableFrame::standard_collapsable": {
            "background_color": 0xFF343432,
            "secondary_color": 0xFF343432,
            "font_size": 16,
            "border_radius": 2.0,
            "border_color": 0x0,
            "border_width": 0,
            
        "CollapsableFrame:hovered:standard_collapsable": {"secondary_color": 0xFFFBF1E5},
        "CollapsableFrame:pressed:standard_collapsable": {"secondary_color": 0xFFF7E4CC},
        
        },
        "ScrollingFrame":{
            #"background_color": 0xFF343432,
            #"secondary_color": 0xFF343432,
            "font_size": 16,
            "border_radius": 2.0,
            "border_color": 0x0,
            "border_width": 0,
            "padding": 16,
        },
        #-----------------------------------------------------------------------------------------------------
        "Label::transform": {"font_size": 12, "color": 0xFF8A8777},
        "Label::transform_label": {"font_size": 12, "color": 0xFFDDDDDD},
        "Label": {"font_size": 12, "color": 0xFF8A8777},
        "Label::label": {"font_size": 14, "color": 0xFF8A8777},
        "Label::title": {"font_size": 14, "color": 0xFFAAAAAA},
        #-----------------------------------------------------------------------------------------------------
        "ComboBox::path": {"font_size": 12, "secondary_color": 0xFF23211F, "color": 0xFFAAAAAA},
        "ComboBox::choices": {
            "font_size": 12,
            "color": 0xFFAAAAAA,
            "background_color": 0xFF23211F,
            "secondary_color": 0xFF23211F,
        },
        "ComboBox:hovered:choices": {"background_color": 0xFF33312F, "secondary_color": 0xFF33312F},
        #-----------------------------------------------------------------------------------------------------
        "Slider::transform": {
            "background_color": 0xFF23211F,
            "border_radius": 3,
            "draw_mode": ui.SliderDrawMode.DRAG,
            "corner_flag": ui.CornerFlag.RIGHT,
            "font_size": 14,
        },
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
        "Slider::colorField": {"background_color": 0xFF23211F, "font_size": 14, "color": 0xFF8A8777},
        #-----------------------------------------------------------------------------------------------------
        "CheckBox::greenCheck": {"font_size": 10, "background_color": KIT_GREEN, "color": 0xFF23211F},
        "CheckBox::whiteCheck": {"font_size": 10, "background_color": 0xFFDDDDDD, "color": 0xFF23211F},
        #-----------------------------------------------------------------------------------------------------
        "Field::models": {"background_color": 0xFF23211F, "font_size": 12, "color": 0xFFAAAAAA, "border_radius": 4.0},
        "Field::transform": {
            "background_color": 0xFF23211F,
            "border_radius": 3,
            "corner_flag": ui.CornerFlag.RIGHT,
            "font_size": 12,
        },
        
        "StringField": {
                        "background_color": 0xFF23211F, 
                        "font_size": 12, 
                        "color": 0xFFAAAAAA, 
                        "border_radius": 2,
                        "padding": 3,
                        "margin": 3,
                        "border_width": 0,
                        "height": 10
        },
        "StringField:focused": {
            "background_color": 0xFF33312F,
            "border_color": 0xFF8A8777,
            "border_width": 1,
            "height": 10
        },
    }
    
    return DARK_WINDOW_STYLE

def collapbsable_style():
    
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
    
    return CollapsableFrame_style