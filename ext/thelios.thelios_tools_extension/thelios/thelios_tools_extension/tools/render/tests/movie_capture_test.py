import omni.kit

sequence = True

start_frame = 1
end_frame = 2
single_frame = 3

def start_capture_extension_render():

    if sequence == True:
        _start_frame = start_frame
        _end_frame = end_frame
    else:
        _start_frame = single_frame
        _end_frame = single_frame
        
    print(f"Start frame: {start_frame}")
    print(f"End frame: {end_frame}")
    
    capture_extension = omni.kit.capture.viewport.CaptureExtension.get_instance()
    capture_extension.options._output_folder = r'C:/Users/l.scattolin/Desktop/'
    capture_extension.options._file_type = '.png'
    capture_extension.options._save_alpha = True
    capture_extension.options._res_width = 1920
    capture_extension.options._res_height = 1920
    capture_extension.options._path_trace_spp = 256
    capture_extension.options._preroll_frames = 0  # meno attesa per un singolo frame
    capture_extension.options._start_frame = _start_frame
    capture_extension.options._end_frame = _end_frame      # stesso frame per singolo render
    capture_extension.options._overwrite_existing_frames = True
    capture_extension.options._file_name = "Fanculo"
    capture_extension.options._file_name_num_pattern = ".##"
    capture_extension.options._render_product = True
    capture_extension.start()
        
start_capture_extension_render()