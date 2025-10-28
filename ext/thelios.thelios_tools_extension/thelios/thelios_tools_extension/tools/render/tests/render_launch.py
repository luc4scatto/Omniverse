import omni.ui as ui
import omni.kit
from omni.kit.window.popup_dialog import MessageDialog
from omni.kit.widget.prompt import Prompt
import omni.kit.usd.layers as layers

import asyncio
import carb
import os

from pxr import UsdRender

CAPTURE_FILE_NUM_PATTERN = (".####",)
CAPTURE_FILE_TYPES = [".tga", ".png", ".exr"]
TYPE_INDEX_OF_PNG = 1
VIDEO_FRAMES_DIR_NAME = "frames"
DEFAULT_IMAGE_FRAME_TYPE_FOR_VIDEO = ".png"
DEFAULT_VIDEO_SECONDS = 2
ICON_SIZE = 13
DEFAULT_CAPTURE_TYPE_SETTING_PATH = "/exts/omni.kit.window.movie_capture/default_capture_type"
RENDER_PRODUCT_CAPTURE_SETTING_PATH = "/exts/omni.kit.window.movie_capture/render_product_enabled"
RENDER_PRESET_SUPPORT_RENDER_PRODUCT_SETTING_PATH = (
    "/exts/omni.kit.window.movie_capture/render_preset_support_render_product"
)

LIVE_SESSION_RESTRICTION_WARNING = "We currently do not support submitting renders during a live-session, due to the dynamic nature of the shared scene."



capture_instance = omni.kit.capture.viewport.CaptureExtension.get_instance()    
_usd_context = omni.usd.get_context()

_ui_kit_capture_type = ui.ComboBox(
                    TYPE_INDEX_OF_PNG, *CAPTURE_FILE_TYPES, identifier="output_setting_id_combo_capture_type")

_ui_kit_path = ui.StringField(identifier="output_setting_id_stringfield_path")

def is_in_live_session() -> bool:
    usd_context = omni.usd.get_context()
    live_syncing = layers.get_layers(usd_context).get_live_syncing()
    return live_syncing.is_stage_in_live_session()

def _on_render_product_conflict_popup_yes_clicked(dialog):
        dialog.hide()
        
def _get_combobox_value(combobox, values_tuple):
    index = combobox.model.get_item_value_model().as_int
    return values_tuple[index]

_ui_kit_default_capture_name = ui.StringField(
                    width=ui.Percent(50), height=0, identifier="output_setting_id_stringfield_default_capture_name"
                )

def _check_render_product_and_exr():
        if (
            capture_instance.options.file_type != ".exr"
            and len(capture_instance.options.render_product) > 0
        ):
            reason_str = "Render product only works with .exr files now. "
            fact_str = f"Render product is set to {capture_instance.options.render_product} and output file format is set to {capture_instance.options.file_type}. "
            action_str = "Please double check the two settings."
            dialog = MessageDialog(
                parent=None,
                title="Movie Capture - render product capture",
                message=f"{reason_str}{fact_str}{action_str}",
                ok_handler=_on_render_product_conflict_popup_yes_clicked,
                ok_label="OK",
                disable_cancel_button=True,
            )
            dialog.show()
            return True
        return False

def __initiate_capture(skip_check: bool = False):
    
    if not skip_check and _check_render_product_and_exr() is True:
        return False
    
    render_prod = capture_instance.options.render_product
    if render_prod:
        stage = _usd_context.get_stage()
        usd_rp = UsdRender.Product(stage.GetPrimAtPath(render_prod))
        if not usd_rp:
            carb.log_error(f"{render_prod} is not a UsdRender.Product")
            return False
        
        came_rel = usd_rp.GetCameraRel()
        previous_targets = usd_rp.GetCameraRel().GetTargets()
        came_rel.SetTargets([capture_instance.options.camera])
        
        def restore_targets():
            if previous_targets:
                came_rel.SetTargets(previous_targets)
            else:
                came_rel.ClearTargets(False)
                
        capture_instance.capture_finished_fn = restore_targets
        
    capture_instance.start()
    return True

def _on_overwrite_mp4_popup_yes_clicked(dialog):
        dialog.hide()
        __initiate_capture(True)

def _on_capture_sequence_clicked(self):
    if is_in_live_session():
        Prompt(title="Movie Capture unavailable", text=LIVE_SESSION_RESTRICTION_WARNING, modal=True).show()
        return
    """
    if not self._check_output_path():
        return
    """
    capture_options, _ = self._collect_capture_settings_fn(to_capture_sequence=True, to_send_to_farm=False)
    if capture_options is None:
        return
    # if mp4 type to check if the result file is exist or not, and warn it
    file_type = _get_combobox_value(_ui_kit_capture_type, CAPTURE_FILE_TYPES)
    mp4_path = os.path.join(
        _ui_kit_path.model.as_string, _ui_kit_default_capture_name.model.as_string + file_type
    )
    if file_type == ".mp4" and os.path.exists(mp4_path):
        dialog = MessageDialog(
            parent=None,
            title="Movie Capture - MP4 file exists",
            message=f"The MP4 file {mp4_path} exists already. Do you want to overwrite it?",
            ok_handler=_on_overwrite_mp4_popup_yes_clicked,
            ok_label="Yes",
            cancel_label="No",
        )
        dialog.show()
    else:
        __initiate_capture()
        
def _read_kit_capture_options(
        self, to_capture_sequence, to_send_to_farm=False
    ) -> typing.Tuple[CaptureOptions, typing.Dict]:
        # refresh the options as we don't want to keep options from last run, like the early quit time limit for Farm option
        self._capture_instance.options = CaptureOptions()
        if not read_kit_capture_options(
            self._capture_instance.options,
            to_capture_sequence,
            self._capture_settings_widget,
            self._render_settings_widget,
            self._output_settings_widget,
            self._farm_settings_widget,
            to_send_to_farm,
        ):
            return None, None

        metadata = {}
        # Handle optional advanced rendering features for metadata:
        task_extensions = self._farm_settings_widget.get_task_extensions()
        if task_extensions is not None:
            metadata["extensions"] = task_extensions
        task_registries = self._farm_settings_widget.get_task_registries()
        if task_registries is not None:
            metadata["registries"] = self._farm_settings_widget.get_task_registries()

        farm_data = {
            "farm_url": self._farm_settings_widget.get_selected_farm(),
            "task_type": self._farm_settings_widget.get_task_type(),
            "start_delay": self._farm_settings_widget.get_start_delay(),
            "batch_count": self._farm_settings_widget.get_batch_count(),
            "task_comment": self._farm_settings_widget.get_task_comment(),
            "priority": self._farm_settings_widget.get_task_priority(),
            "metadata": metadata,
            "bad_frame_size_threshold": self._farm_settings_widget.get_task_valid_frame_size(),
            "max_bad_frame_threshold": self._farm_settings_widget.get_task_frame_size_threshold(),
            "texture_streaming_memory_budget": self._farm_settings_widget.get_texture_streaming_memory_budget(),
        }

        # Handle optional advanced rendering features for farm data:
        upload_to_s3 = self._farm_settings_widget.get_upload_to_s3()
        if upload_to_s3 is not None:
            farm_data["upload_to_s3"] = upload_to_s3
        skip_upload = self._farm_settings_widget.get_skip_upload_to_s3()
        if skip_upload is not None:
            farm_data["skip_upload"] = skip_upload

        if not self._is_default_scene():
            UIValuesInterface().save_ui_values(
                self._capture_settings_widget,
                self._render_settings_widget,
                self._output_settings_widget,
                self._farm_settings_widget,
            )
        return self._capture_instance.options, farm_data