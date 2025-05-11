
import trimesh
import plotly.graph_objects as go

class Model:
    
    def __init__(self, model_path='./assets/lego_man.glb'):
        
        # Try loading the 3D model
        try:
            scene = trimesh.load(model_path)
            self.__mesh_data = scene.to_geometry()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

        # Create Plotly 3D mesh
        self.__mesh = go.Mesh3d(
            x=self.__mesh_data.vertices[:, 0],
            y=self.__mesh_data.vertices[:, 1],
            z=self.__mesh_data.vertices[:, 2],
            i=self.__mesh_data.faces[:, 0],
            j=self.__mesh_data.faces[:, 1],
            k=self.__mesh_data.faces[:, 2],
            opacity=0.5,
            color='lightblue',
            flatshading=True
        )

        #A Plotly figure with the 3D mesh
        self.figure = go.Figure(data=[self.__mesh])
        self.figure.update_layout(
            scene=dict(
                xaxis=dict(title='X'),
                yaxis=dict(title='Y'),
                zaxis=dict(title='Z'),
                aspectmode='data'
            ),
            #title='3D Lego Model Visualization',
            margin=dict(l=0, r=0, b=0, t=30)
        )

    def update_mesh(self, mesh: go.Mesh3d) -> None:
        if not isinstance(mesh, go.Mesh3d):
            raise TypeError('Mesh must be a go.Mesh3d type')
        
        self.__mesh = mesh

    def get_mesh(self) -> go.Mesh3d:
        return self.__mesh
    
    def get_mesh_data(self):
        return self.__mesh_data
    

    