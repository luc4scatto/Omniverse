# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
"""an example of creating a custom attribute Editor window"""
from omni import ui
from pathlib import Path

ICON_PATH = Path(__file__).parent.parent.joinpath("icons")

LIGHT_WINDOW_STYLE = {
    # main frame style
    "ScrollingFrame::canvas": {"background_color": 0xFFCACACA},
    "Frame::main_frame": {"background_color": 0xFFCACACA},
    # title bar style
    "Label::title": {"color": 0xFF777777, "font_size": 16.0},
    "Rectangle::titleBar": {"background_color": 0xFFCACACA},
    "Rectangle::timeSelection": {"background_color": 0xFF888888, "border_radius": 5.0},
    "Triangle::timeArrows": {"background_color": 0xFFCACACA},
    "Label::timeLabel": {"color": 0xFFDDDDDD, "font_size": 16.0},
    # custom widget slider
    "Rectangle::sunStudySliderBackground": {
        "background_color": 0xFFBBBBBB,
        "border_color": 0xFF888888,
        "border_width": 1.0,
        "border_radius": 10.0,
    },
    "Rectangle::sunStudySliderForground": {"background_color": 0xFF888888},
    "Circle::slider": {"background_color": 0xFFBBBBBB},
    "Circle::slider:hovered": {"background_color": 0xFFCCCCCC},
    "Circle::slider:pressed": {"background_color": 0xFFAAAAAA},
    "Triangle::selector": {"background_color": 0xFF888888},
    "Triangle::selector:hovered": {"background_color": 0xFF999999},
    "Triangle::selector:pressed": {"background_color": 0xFF777777},
    # toolbar
    "Triangle::play_button": {"background_color": 0xFF6E6E6E},
}

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
        "padding": 0,
    },
    "HStack::header": {"margin": 5},
    "CollapsableFrame:hovered": {"secondary_color": 0xFF3A3A3A},
    "CollapsableFrame:pressed": {"secondary_color": 0xFF343432},
}


class AttributeEditorWindow:
    """ example of an Attribute Editor Window using Omni::UI """

    def __init__(self):
        self._editor_window = None
        self._window_Frame = None

    def set_style_light(self, button):
        """ """
        self._window_Frame.set_style(LIGHT_WINDOW_STYLE)

    def set_style_dark(self, button):
        """ """
        self._window_Frame.set_style(DARK_WINDOW_STYLE)

    def shutdown(self):
        """Should be called when the extesion us unloaded"""
        # Unfortunatley, the member variables are not destroyed when the extension is unloaded. We need to do it
        # automatically. Usually, it's OK because the Python garbage collector will eventually destroy everythigng. But
        # we need the images to be destroyed right now because Kit know nothing about Python garbage collector and it
        # will fire warning that texture is not destroyed.
        self._editor_window = None

    def _create_object_selection_frame(self):
        with ui.Frame():
            with ui.ZStack():
                ui.Rectangle(name="frame_background")
                with ui.VStack(spacing=5, name="this", style={"VStack::this": {"margin": 5, "margin_width": 15}}):
                    with ui.HStack(height=0):
                        ui.StringField(name="models").model.set_value("(9 models selected)")
                        with ui.VStack(width=0, height=0):
                            ui.Spacer(width=0, height=3)
                            ui.Image(
                                "resources/glyphs/lock_open.svg",
                                width=25,
                                height=12,
                                style={"color": KIT_GREEN, "marging_width": 5},
                            )
                            ui.Spacer(width=0)
                        with ui.VStack(width=0, height=0):
                            ui.Spacer(width=0, height=3)
                            ui.Image("resources/glyphs/settings.svg", width=25, height=12, style={"color": KIT_GREEN})
                            ui.Spacer(width=0)

                    with ui.HStack(height=0):
                        with ui.ZStack(width=60):
                            ui.Image(f"{ICON_PATH}/Add.svg", width=60, height=30)
                            with ui.HStack(name="this", style={"HStack::this": {"margin_height": 0}}):
                                ui.Spacer(width=15)
                                ui.Label("Add", style={"font_size": 16, "color": 0xFFAAAAAA, "margin_width": 10})
                        ui.Spacer(width=50)
                        with ui.ZStack():
                            ui.Rectangle(style={"background_color": 0xFF23211F, "border_radius": 4.0})
                            with ui.HStack():
                                with ui.VStack(width=0):
                                    ui.Spacer(width=0)
                                    ui.Image("resources/glyphs/sync.svg", width=25, height=12)
                                    ui.Spacer(width=0)
                                ui.StringField(name="models").model.set_value("Search")

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
                    ui.Circle(width=10, height=20, style={"background_color": 0xFF555555})
            ui.ComboBox(0, paths, paths, name="path", width=0, height=0, arrow_only=True)
            ui.Spacer(width=5)
            ui.Image("resources/icons/folder.png", width=15)
            ui.Spacer(width=5)
            ui.Image("resources/icons/find.png", width=15)
            self._create_control_state(2)

    def _build_transform_frame(self):
        # Transform Frame
        with ui.CollapsableFrame(title="Transform", style=CollapsableFrame_style):
            with ui.VStack(spacing=8, name="frame_v_stack"):
                ui.Spacer(height=0)
                components = ["Position", "Rotation", "Scale"]
                for component in components:
                    with ui.HStack():
                        with ui.HStack(width=LABEL_PADDING):
                            ui.Label(component, name="transform", width=50)
                            self._create_control_state()
                            ui.Spacer()
                        # Field (X)
                        all_axis = ["X", "Y", "Z"]
                        colors = {"X": 0xFF5555AA, "Y": 0xFF76A371, "Z": 0xFFA07D4F}
                        for axis in all_axis:
                            with ui.HStack():
                                with ui.ZStack(width=15):
                                    ui.Rectangle(
                                        width=15,
                                        height=20,
                                        style={
                                            "background_color": colors[axis],
                                            "border_radius": 3,
                                            "corner_flag": ui.CornerFlag.LEFT,
                                        },
                                    )
                                    ui.Label(axis, name="transform_label", alignment=ui.Alignment.CENTER)
                                ui.FloatDrag(name="transform", min=-1000000, max=1000000, step=0.01)
                                self._create_control_state(0)
                ui.Spacer(height=0)

    def _build_checked_header(self, collapsed, title):
        triangle_alignment = ui.Alignment.RIGHT_CENTER
        if not collapsed:
            triangle_alignment = ui.Alignment.CENTER_BOTTOM

        with ui.HStack(style={"HStack": {"margin_width": 15, "margin_height": 5}}):
            with ui.VStack(width=20):
                ui.Spacer()
                ui.Triangle(
                    alignment=triangle_alignment,
                    name="title",
                    width=8,
                    height=8,
                    style={"background_color": 0xFFCCCCCC},
                )
                ui.Spacer()

            ui.Label(title, name="title", width=0)
            ui.Spacer()
            ui.CheckBox(width=10, name="whiteCheck").model.set_value(True)
            self._create_control_state()

    def _build_custom_callapsable_frame(self):
        with ui.CollapsableFrame(
            title="Light Property", style=CollapsableFrame_style, build_header_fn=self._build_checked_header
        ):
            with ui.VStack(spacing=12, name="frame_v_stack"):
                ui.Spacer(height=5)
                with ui.HStack():
                    ui.Label("Slider", name="label", width=LABEL_PADDING)
                    ui.IntSlider(name="value_less", min=0, max=100, usingGauge=True).model.set_value(30)
                    self._create_control_state()

                self._create_checkbox_control("Great UI", True)
                self._create_checkbox_control("Hard To Build", False)
                self._create_checkbox_control("Support very very very long checkbox label", True)
                ui.Spacer(height=0)

    def _build_dropdown_frame(self):
        with ui.Frame():
            with ui.ZStack():
                ui.Rectangle(name="frame_background")
                with ui.VStack(height=0, spacing=10, name="frame_v_stack"):
                    ui.Spacer(height=5)
                    for index in range(3):
                        with ui.HStack():
                            ui.Label("Drop Down", name="label", width=LABEL_PADDING)
                            ui.ComboBox(0, "Choice 1", "Choice 2", "Choice 3", height=10, name="choices")
                            self._create_control_state()

                    self._create_checkbox_control("Check Box", False)
                    ui.Spacer(height=0)

    def _build_scale_and_bias_frame(self):
        with ui.CollapsableFrame(title="Scale And Bias Output", collapsed=False, style=CollapsableFrame_style):
            with ui.VStack(name="frame_v_stack"):
                with ui.HStack():
                    ui.Spacer(width=100)
                    ui.Label("Scale", name="label", alignment=ui.Alignment.CENTER)
                    ui.Spacer(width=10)
                    ui.Label("Bias", name="label", alignment=ui.Alignment.CENTER)

                with ui.VStack(spacing=8):
                    colors = ["Red", "Green", "Blue", "Alpha"]
                    for color in colors:
                        with ui.HStack():
                            ui.Label(color, name="label", width=LABEL_PADDING)
                            ui.FloatSlider(name="value", min=0, max=2).model.set_value(1.0)
                            self._create_control_state(6)
                            ui.Spacer(width=20)
                            ui.FloatSlider(name="value", min=-1.0, max=1.0).model.set_value(0.0)
                            state = None
                            if color == "Red":
                                state = 2
                            elif color == "Blue":
                                state = 5
                            else:
                                state = 3
                            self._create_control_state(state)
                    ui.Spacer(height=0)

                ui.Spacer(height=5)
                with ui.VStack(spacing=14):
                    self._create_checkbox_control("Warp to Output Range", True)

                    ui.Line(style={"color": KIT_GREEN})

                    self._create_checkbox_control("Border Color", True)
                    self._create_checkbox_control("Zero Alpha Border", False)
                    with ui.HStack():
                        self._create_checkbox_control("Cutout Alpha", False, label_width=20, line_width=20)
                        self._create_checkbox_control("Scale Alpha For Mi Pmap Coverage", True)
                    self._create_checkbox_control("Border Color", True)
                    ui.Spacer(height=0)

    def _build_color_picker_frame(self):
        def color_drag(args):
            with ui.HStack(spacing=2):
                color_model = ui.MultiFloatDragField(
                    args[0], args[1], args[2], width=200, h_spacing=5, name="colorField"
                ).model
                ui.ColorWidget(color_model, width=10, height=10)

        def color4_drag(args):
            with ui.HStack(spacing=2):
                color_model = ui.MultiFloatDragField(
                    args[0],
                    args[1],
                    args[2],
                    args[3],
                    width=200,
                    h_spacing=5,
                    style={"color": 0xFFAAAAAA, "background_color": 0xFF000000, "draw_mode": ui.SliderDrawMode.HANDLE},
                ).model
                ui.ColorWidget(color_model, width=10, height=10)

        with ui.CollapsableFrame(title="Color Controls", collapsed=False, style=CollapsableFrame_style):
            with ui.VStack(name="frame_v_stack"):
                with ui.VStack(spacing=8):
                    colors = [("Red", [1.0, 0.0, 0.0]), ("Green", [0.0, 1.0, 0.0]), ("Blue", [0.0, 0.0, 1.0])]

                    for color in colors:
                        with ui.HStack():
                            ui.Label(color[0], name="label", width=LABEL_PADDING)
                            if len(color[1]) == 4:
                                color4_drag(color[1])
                            else:
                                color_drag(color[1])

                            self._create_control_state(0)

                    ui.Line(style={"color": 0x338A8777})

                    color = ("RGBA", [1.0, 0.0, 1.0, 0.5])
                    with ui.HStack():
                        ui.Label(color[0], name="label", width=LABEL_PADDING)
                        color4_drag(color[1])
                        self._create_control_state(0)
                    ui.Spacer(height=0)

    def _build_frame_with_radio_button(self):
        with ui.CollapsableFrame(title="Compression Quality", collapsed=False, style=CollapsableFrame_style):
            with ui.VStack(spacing=8, name="frame_v_stack"):
                ui.Spacer(height=5)
                with ui.HStack():
                    with ui.VStack(width=LABEL_PADDING):
                        ui.Label("  Select One...", name="label", width=100, height=0)
                        ui.Spacer(width=100)

                    with ui.VStack(spacing=10):
                        values = ["Faster", "Normal", "Production", "Highest"]

                        for value in values:
                            with ui.HStack():
                                with ui.ZStack(width=20):
                                    outer_style = {
                                        "border_width": 1,
                                        "border_color": KIT_GREEN,
                                        "background_color": 0x0,
                                        "border_radius": 2,
                                    }
                                    ui.Rectangle(width=12, height=12, style=outer_style)

                                    if value == "Faster":
                                        outer_style = {"background_color": KIT_GREEN, "border_radius": 2}
                                        with ui.Placer(offset_x=3, offset_y=3):
                                            ui.Rectangle(width=10, height=10, style=outer_style)

                                ui.Label(value, name="label", aligment=ui.Alignment.LEFT)
                ui.Spacer(height=0)

    def build_window(self):
        """ build the window for the Class"""
        self._editor_window = ui.Window("Attribute Editor", width=450, height=800)
        self._editor_window.deferred_dock_in("Layers")
        self._editor_window.setPosition(0, 0)
        self._editor_window.frame.set_style(DARK_WINDOW_STYLE)
        with self._editor_window.frame:
            with ui.VStack():
                with ui.HStack(height=20):
                    ui.Label("Styling :  ", alignment=ui.Alignment.RIGHT_CENTER)
                    ui.Button("Light Mode", clicked_fn=lambda b=None: self.set_style_light(b))
                    ui.Button("Dark Mode", clicked_fn=lambda b=None: self.set_style_dark(b))
                    ui.Spacer()
                ui.Spacer(height=10)
                self._window_Frame = ui.ScrollingFrame(
                    name="canvas",
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                )
                with self._window_Frame:
                    with ui.VStack(height=0, name="main_v_stack", spacing=6):

                        # create object selection Frame
                        self._create_object_selection_frame()

                        # create build transform Frame
                        self._build_transform_frame()

                        # DropDown Frame
                        self._build_dropdown_frame()

                        # Custom Collapsable Frame
                        self._build_custom_callapsable_frame()

                        # Custom Collapsable Frame
                        with ui.CollapsableFrame(title="Files", style=CollapsableFrame_style):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                ui.Spacer(height=0)
                                self._create_path_combo("UI Path", "omni:/Project/Cool_ui.usd")
                                self._create_path_combo("Texture Path", "omni:/Project/cool_texture.png")
                                ui.Spacer(height=0)

                        # Custom Collapsable Frame
                        with ui.CollapsableFrame(title="Images Options", collapsed=True, style=CollapsableFrame_style):
                            with ui.VStack(spacing=10, name="frame_v_stack"):
                                self._create_path_combo("Images Path", "omni:/Library/Images/")
                                ui.Spacer(height=0)

                        # Custom Collapsable Frame
                        self._build_frame_with_radio_button()

                        # Scale And Bias
                        self._build_scale_and_bias_frame()

                        # Color Pickrs
                        self._build_color_picker_frame()

        return self._editor_window
