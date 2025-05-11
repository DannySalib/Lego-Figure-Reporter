import plotly.graph_objects as go
import numpy as np
from typing import Optional, Tuple
from LegoModel import LegoModel
from ModelUpdater import ModelUpdater

class InteractiveModel:

    default_point_size = 10
    default_point_color = 'red'
    default_highlighted_point_size = default_point_size * 2
    default_highlighted_point_color = 'green'

    def __init__(self, lego_model: LegoModel):
        self.__lego_model = lego_model
        
        # Initialize scatter trace with numpy arrays for better performance      
        self.points = go.Scatter3d(
            x=np.array([], dtype=float),
            y=np.array([], dtype=float),
            z=np.array([], dtype=float),
            mode='markers',  # Fix typo: 'markers' not 'markers'
            marker=dict(
                color=np.array([], dtype=str),
                size=np.array([], dtype=float),
                symbol='circle',
                opacity=1.0,  # Ensure full opacity
                colorscale=None  # Disable colorscale if using direct colors
            ),
            name='Clicked Points'
        )

        # Track XYZ coordinates and their indices
        self.coord_dict: dict[Tuple[float, float, float], int] = {}
        
        # Set up figure
        self.figure = self.__lego_model.get_figure()
        self.figure.add_trace(self.points)
        self.updater = ModelUpdater(self)

    def get_lego_model(self) -> LegoModel:
        return self.__lego_model

    def clear_points(self) -> None:
        """Clear all points"""
        with self.updater:
            self.points.x = np.array([], dtype=float)
            self.points.y = np.array([], dtype=float)
            self.points.z = np.array([], dtype=float)
            self.points.marker.color = np.array([], dtype=str)
            self.points.marker.size = np.array([], dtype=float)
            self.coord_dict.clear()
    
    def add_point(self, x: float, y: float, z: float) -> None:
        """Add a point with O(1) duplicate checking"""
        coord = (x, y, z)
        if coord in self.coord_dict:
            return  # Skip duplicates
            
        with self.updater:
            # Append coordinates (creates new arrays)
            self.points.x = np.append(self.points.x, x)
            self.points.y = np.append(self.points.y, y)
            self.points.z = np.append(self.points.z, z)
            
            # Create new writable arrays for marker properties
            new_colors = np.append(
                np.array(self.points.marker.color, copy=True),
                self.default_point_color
            )
            new_sizes = np.append(
                np.array(self.points.marker.size, copy=True),
                self.default_point_size
            )
            
            # Update the trace
            self.points.marker.color = new_colors
            self.points.marker.size = new_sizes
            
            # Store index
            self.coord_dict[coord] = len(self.points.x) - 1
    
    def get_figure_with_camera(self, camera_state=None):
        """Return figure with optional camera state"""
        fig = self.figure
        if camera_state:
            fig.update_layout(scene_camera=camera_state)
        return fig

    def interact_with_point(self, x: float, y: float, z: float) -> None:
        """Highlight a specific point by changing its color and size"""
        coord = (x, y, z)
        if coord not in self.coord_dict:
            return
            
        point_idx = self.coord_dict[coord]
        
        with self.updater:
            # Create new writable arrays
            new_colors = np.array(self.points.marker.color, copy=True)
            new_sizes = np.array(self.points.marker.size, copy=True)
            
            # Reset all points to defaults
            new_colors[:] = self.default_point_color
            new_sizes[:] = self.default_point_size
            
            # Highlight the selected point
            new_colors[point_idx] = self.default_highlighted_point_color
            new_sizes[point_idx] = self.default_highlighted_point_size
            
            # Update the trace
            self.points.marker.color = new_colors
            self.points.marker.size = new_sizes