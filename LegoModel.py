
import trimesh
import plotly.graph_objects as go

class LegoModel:
    
    def __init__(self, model_path='lego_man.glb'):
        
        # Try loading the 3D model
        try:
            scene = trimesh.load(model_path)
            _mesh = scene.to_geometry()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

        # Create Plotly 3D mesh
        self.__mesh = go.Mesh3d(
            x=_mesh.vertices[:, 0],
            y=_mesh.vertices[:, 1],
            z=_mesh.vertices[:, 2],
            i=_mesh.faces[:, 0],
            j=_mesh.faces[:, 1],
            k=_mesh.faces[:, 2],
            opacity=0.5,
            color='lightblue',
            flatshading=True
        )

        #A Plotly figure with the 3D mesh
        self.__fig = go.Figure(data=[self.__mesh])
        self.__fig.update_layout(
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z'),
                aspectmode='data'
            ),
            #title='3D Lego Model Visualization',
            margin=dict(l=0, r=0, b=0, t=30)
        )
        
    def get_figure(self) -> go.Figure:
        """Return a Plotly figure with the 3D mesh"""
        return self.__fig

    def get_mesh(self) -> go.Mesh3d:
        """Return a Plotly 3D mesh"""
        return self.__mesh