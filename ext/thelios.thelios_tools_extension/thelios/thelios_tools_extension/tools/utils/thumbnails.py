import omni.kit.viewport.utility as vp_utils
from pxr import UsdGeom, Gf, UsdShade, Sdf
import omni.usd
import asyncio
import os

class MaterialThumbnailGenerator:
    def __init__(self):
        self.stage = omni.usd.get_context().get_stage()
        
    async def generate_thumbnail(self, material_path: str, output_path: str):
        """
        Generate thumbnail for MaterialX OpenPBR:
        1. Create test scene (sphere + light + camera)
        2. Apply material
        3. Capture viewport
        4. Cleanup
        """
        # 1. Create minimal test scene
        await self._create_test_scene()
        
        # 2. Apply material to sphere
        self._apply_material_to_sphere(material_path)
        
        # 3. Setup camera/light for perfect material preview
        self._setup_render_view()
        
        # 4. Capture thumbnail (256x256 PNG)
        await self._capture_thumbnail(output_path)
        
        # 5. Cleanup
        self._cleanup_scene()
        
        print(f"✅ Thumbnail saved: {output_path}")
    
    async def _create_test_scene(self):
        """Create sphere, dome light, camera."""
        # Sphere for material preview
        sphere = UsdGeom.Sphere.Define(self.stage, "/World/PreviewSphere")
        sphere.CreateRadiusAttr(1.0)
        
        # Dome light (HDRI neutral)
        dome = UsdGeom.DomeLight.Define(self.stage, "/World/DomeLight")
        dome.CreateTextureFileAttr("omni_pbr://textures/omni_pbr_white_neutral_2k.hdr")
        dome.CreateColorAttr(Gf.Vec3f(1, 1, 1))
        dome.CreateIntensityAttr(1000.0)
        
        # Ortho camera front-on
        camera = UsdGeom.Camera.Define(self.stage, "/World/Camera")
        camera.CreateFocalLengthAttr(35.0)
        camera.CreateHorizontalApertureAttr(20.955)
        camera.CreateVerticalApertureAttr(15.290)
        xform = UsdGeom.Xformable(camera.GetPrim())
        xform.AddTranslateOp().Set(Gf.Vec3f(0, 0, 5))
        xform.AddRotateXOp().Set(-10.0)
    
    def _apply_material_to_sphere(self, material_path: str):
        """Bind material to preview sphere."""
        sphere_prim = self.stage.GetPrimAtPath("/World/PreviewSphere")
        material_prim = self.stage.GetPrimAtPath(material_path)
        material = UsdShade.Material(material_prim)
        
        binding_api = UsdShade.MaterialBindingAPI.Apply(sphere_prim)
        binding_api.Bind(material)
    
    async def _setup_render_view(self):
        """Frame material perfectly."""
        viewport = omni.ui.Workspace.get_window("Viewport").get_viewport_api()
        viewport.set_active_camera("/World/Camera")
        viewport.frame_selected([Sdf.Path("/World/PreviewSphere")], 1.2)
        
        # Wait for render
        await asyncio.sleep(0.5)
    
    async def _capture_thumbnail(self, output_path: str):
        """Capture 256x256 PNG."""
        
        # Ensure output dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        viewport_api = omni.ui.Workspace.get_window("Viewport").get_viewport_api()
        future = vp_utils.capture_viewport_to_file(
            viewport_api,
            output_path,
            is_hdr=False,
            format_desc={"resolution": [256, 256]}
        )
        await future
    
    def _cleanup_scene(self):
        """Remove test scene."""
        for path in ["/World/PreviewSphere", "/World/DomeLight", "/World/Camera"]:
            prim = self.stage.GetPrimAtPath(path)
            if prim.IsValid():
                prim.SetActive(False)

# 🔧 USAGE
generator = MaterialThumbnailGenerator()
asyncio.run(generator.generate_thumbnail(
    "/World/Looks/MyMaterialX", 
    "thumbnails/MyMaterialX_thumb.png"
))
