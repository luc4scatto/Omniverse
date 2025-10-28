import omni.ui as ui
from . import constants

class TheliosWindowModel:
    def __init__(self): 
        self.release_model = ui.SimpleIntModel(constants.DEFAULT_RELEASE)
        #self.frame_model = ui.SimpleIntModel(constants.DEFAULT_FRAME)
        self.int_filter_model = ui.SimpleIntModel(constants.DEFAULT_RELEASE)
        self.model_model = ui.SimpleStringModel()
        self.brand_string_model = ui.SimpleStringModel()
        self.type_string_model = ui.SimpleStringModel()

        self.startfr_model = ui.SimpleIntModel(constants.START_FRAME)
        self.endfr_model = ui.SimpleIntModel(constants.END_FRAME)
        self.singlefr_model = ui.SimpleIntModel(constants.END_FRAME)

        self.sequence_model = ui.SimpleBoolModel(constants.SEQUENCE)

        #self._timeline = omni.timeline.get_timeline_interface()
        #self._current_fps = self._timeline.get_time_codes_per_seconds()