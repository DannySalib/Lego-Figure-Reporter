from Model import Model
        
from PIL import Image 
import numpy as np
import plotly.graph_objects as go

class TextureMapper:
    def __init__(self, texture_path: str):
        
        # load texture 
        try:
            self.img = Image.open(texture_path)
            self.img_arr = np.array(self.img)
        except Exception as e:
            print(f"Error loading texture: {e}")
            raise 

    def apply_texture(self, model: Model) -> None:
        return
        # TODO explore alternative strategies, this one is ass 
        mesh_data = model.get_mesh_data()

        # Get model dimensions
        vertices = mesh_data.vertices
        x_min, x_max = vertices[:, 0].min(), vertices[:, 0].max()
        y_min, y_max = vertices[:, 1].min(), vertices[:, 1].max()

        # Calculate aspect ratios
        model_width = x_max - x_min
        model_height = y_max - y_min
        model_ratio = model_width / model_height

        # Load and prepare texture
        img_ratio = self.img.width / self.img.height

        # Resize image to match model aspect ratio
        if not np.isclose(model_ratio, img_ratio, rtol=0.01):
            new_height = int(self.img.width / model_ratio)
            self.img = self.img.resize((self.img.width, new_height), Image.LANCZOS)

        img_arr = np.array(self.img)
        h, w = img_arr.shape[:2]

        # Generate perfect UV coordinates
        u = (vertices[:, 0] - x_min) / model_width
        v = (vertices[:, 1] - y_min) / model_height

        # Ensure perfect 1:1 mapping
        uv_coords = np.stack([u, 1 - v], axis=1)  # Flip V coordinate for image space

        # Convert to texture indices with exact mapping
        u_indices = np.clip((uv_coords[:, 0] * (w - 1)), 0, w - 1).astype(int)
        v_indices = np.clip((uv_coords[:, 1] * (h - 1)), 0, h - 1).astype(int)

        # Sample texture
        colors = img_arr[v_indices, u_indices] / 255.0

        # Create Plotly 3D mesh
        mesh = go.Mesh3d(
            x=mesh_data.vertices[:, 0],
            y=mesh_data.vertices[:, 1],
            z=mesh_data.vertices[:, 2],
            i=mesh_data.faces[:, 0],
            j=mesh_data.faces[:, 1],
            k=mesh_data.faces[:, 2],
            opacity=1,
            vertexcolor=colors,  # or facecolor=face_colors
            flatshading=True,
            # Add this for better color display:
            intensitymode='vertex',  # or 'cell' if using face colors
            showscale=False
        )

        model.update_figure(mesh)