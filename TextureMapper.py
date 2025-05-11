from Model import Model
        
from PIL import Image 
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans

class TextureMapper:
    def __init__(self, texture_path: str):
        
        # load texture 
        try:
            self.texture = Image.open(texture_path).convert('RGB')
            self.texture_array = np.array(self.texture)
        except Exception as e:
            print(f"Error loading texture: {e}")
            raise 

    def apply_texture(self, model: Model) -> None:
        # Step 1: Extract dominant colors from the texture
        dominant_colors = self._extract_dominant_colors(n_colors=5)
        
        # Step 2: Assign colors to mesh vertices based on Y-coordinate (simple segmentation)
        mesh_data = model.get_mesh_data()
        vertices = mesh_data.vertices
        colors = self._assign_colors_based_on_height(vertices, dominant_colors)
        
        # Step 3: Update the mesh with vertex colors
        textured_mesh = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=mesh_data.faces[:, 0],
            j=mesh_data.faces[:, 1],
            k=mesh_data.faces[:, 2],
            vertexcolor=colors,
            opacity=1.0,
            flatshading=True
        )
        model.update_mesh(textured_mesh)

    def _extract_dominant_colors(self, n_colors=5):
        """Extract dominant colors from the texture using K-means clustering."""
        pixels = self.texture_array.reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_colors, random_state=42).fit(pixels)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        return [f'rgb({r},{g},{b})' for r, g, b in dominant_colors]

    def _assign_colors_based_on_height(self, vertices, dominant_colors):
        """Assign colors based on Y-coordinate (height) of vertices."""
        y_min, y_max = vertices[:, 1].min(), vertices[:, 1].max()
        y_range = y_max - y_min
        segment_height = y_range / len(dominant_colors)
        
        colors = []
        for y in vertices[:, 1]:
            segment = int((y - y_min) / segment_height)
            segment = min(segment, len(dominant_colors) - 1)  # Ensure valid index
            colors.append(dominant_colors[segment])
        return colors