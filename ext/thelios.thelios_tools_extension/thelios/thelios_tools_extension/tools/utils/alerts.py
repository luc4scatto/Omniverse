from omni.kit.notification_manager import post_notification, NotificationStatus
import omni.kit.notification_manager as nm
import omni.ui as ui
from ..style import style_widgets

DARK_WINDOW_STYLE = style_widgets.window_style()

class AlertWindow():
    """ document Windows classes"""

    def __init__(self):
        self._window_example = None
        self._modal_window_example = None

    def post_notification_info(self, message: str):
        post_notification(  message, 
                            status=NotificationStatus.INFO, 
                            duration=5.0)
        
    def post_notification_warning(self, message: str):
        post_notification(  message, 
                            status=NotificationStatus.WARNING, 
                            duration=5.0)
        
    def alert_with_buttons(self, message, ok_function, cancel_function):
        
        ok_button = nm.NotificationButtonInfo("OK", on_complete=ok_function)
        cancel_button = nm.NotificationButtonInfo("CANCEL", on_complete=cancel_function)
        notification_info = nm.post_notification(
            message,
            hide_after_timeout=False,
            duration=0,
            status=nm.NotificationStatus.WARNING,
            button_infos=[ok_button, cancel_button],
        )    
    
    def create_and_show_modal_window(self, message: str, function):
        if not self._modal_window_example:
            window_flags = ui.WINDOW_FLAGS_NO_RESIZE
            window_flags |= ui.WINDOW_FLAGS_NO_SCROLLBAR
            window_flags |= ui.WINDOW_FLAGS_MODAL
            self._modal_window_example = ui.Window("Warning!", 
                                                    width=300, 
                                                    height=200, 
                                                    flags=window_flags, 
                                                    alignment=ui.Alignment.CENTER, 
                                                    style={"margin": 8})
            
            with self._modal_window_example.frame:
                with ui.VStack():
                    ui.Label(message, alignment=ui.Alignment.CENTER)
                    ui.Spacer(height=4)
                    with ui.HStack(width=150):
                        ui.Button("Yes", 
                                    height=50, 
                                    clicked_fn=function, 
                                    style=DARK_WINDOW_STYLE)
                        ui.Button("No", 
                                    height=50, 
                                    clicked_fn=self.close_modal_window_me, 
                                    style=DARK_WINDOW_STYLE)
                    
        self._modal_window_example.visible = True
        
    def close_modal_window_me(self):
        if self._modal_window_example:
            self._modal_window_example.visible = False