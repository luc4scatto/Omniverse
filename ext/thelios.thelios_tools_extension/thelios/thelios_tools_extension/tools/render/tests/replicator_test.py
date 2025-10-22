import omni.replicator.core as rep

# Remove the default light
default_light = rep.get.prims(path_pattern="/Environment/defaultLight")
with default_light:
    rep.modify.visibility(False)

camera_positions = [(1347,825,1440), (0, 825, 1440),(1440,825,0)]

# Create the lights
distance_light = rep.create.light(rotation=(400,-23,-94), intensity=10000, temperature=6500, light_type="distant")
cylinder_light = rep.create.light(position=(0,0,0),rotation=(0,-180,-180),light_type="disk")

# Create the environment
cone = rep.create.cone(position=(0,100,0), scale=2)
floor = rep.create.cube(position=(0,0,0), scale=(10,0.1,10))
wall1 = rep.create.cube(position=(-450,250,0), scale=(1,5,10))
wall2 = rep.create.cube(position=(0,250,-450), scale=(10,5,1))

#Create the replicator camera
camera = rep.create.camera(position=(1347,825,1440), look_at=(0,100,0), focus_distance=200,f_stop=8)

# Set the renderer to Path Traced
rep.settings.set_render_pathtraced(samples_per_pixel=64)

# Create the render product
render_product  = rep.create.render_product(camera, (1920, 1080))

# Initialize and attach writer
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(output_dir="_subframes_pt_example", rgb=True)
writer.attach([render_product])


# Render 3 frames, with 50 subframes
with rep.trigger.on_frame(num_frames=3, rt_subframes=50):
    with camera:
        rep.modify.pose(position=rep.distribution.sequence(camera_positions), look_at=(0,100,0))