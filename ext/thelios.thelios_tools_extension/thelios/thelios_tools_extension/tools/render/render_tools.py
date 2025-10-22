import omni.kit.viewport.utility as viewport_utility
import omni.kit.movie_capture as movie_capture
import omni.timeline
        
def render_rtx_path_tracing_sequence(export_path, num_frames):
    # Imposta la modalità RTX Interactive Path Tracing
    #viewport_utility.set_render_mode("RTX – Interactive (Path Tracing)")

    timeline = omni.timeline.get_timeline_interface()
    viewport_api = viewport_utility.get_active_viewport()

    for frame in range(num_frames):
        timeline.set_current_time(frame)
        filename = f"{export_path}/frame_{frame:03d}.exr"
        
        # Cattura il contenuto del viewport in formato EXR
        future = viewport_utility.capture_viewport_to_file(
            viewport_api=viewport_api,
            file_path=filename,
            is_hdr=True
        )
        # Attendi il completamento della cattura (opzionale in caso di async)
        # future.wait()  # Se supportato e necessario
        # Puoi aggiungere un breve delay o wait per sicurezza a seconda del workflow
        timeline.set_current_time(frame + 1)
"""        
def capture_sequence_movie(export_path, file_prefix, num_frames):
    # Ottieni l'interfaccia Movie Capture
    capture = movie_capture.get_movie_capture_interface()

    # Configura percorso di output e prefisso file
    capture.set_output_path(export_path)
    capture.set_file_prefix(file_prefix)
    
    # Imposta che il tipo di cattura sia SEQUENCE per image sequence
    capture.set_capture_type(movie_capture.CaptureMovieType.SEQUENCE)
    
    # Imposta la risoluzione (opzionale)
    capture.set_resolution(1920, 1080)
    
    # Avvia la cattura sequenza all'inizio del frame 0
    timeline = omni.timeline.get_timeline_interface()
    timeline.set_current_time(0)
    
    capture.start_movie_capture()

    for frame in range(num_frames):
        timeline.set_current_time(frame)
        # Qui potresti voler inserire delay o wait se necessario per il completamento frame

    capture.stop_movie_capture()
"""    