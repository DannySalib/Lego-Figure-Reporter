class InteractiveModelUpdater:
    def __init__(self, model):
        self.model = model

    def __enter__(self):
        # Save current view state safely
        scene = self.model.figure.layout.scene
        self.original_view = {
            'eye': {'x': scene.camera.eye.x, 'y': scene.camera.eye.y, 'z': scene.camera.eye.z},
            'center': {'x': scene.camera.center.x, 'y': scene.camera.center.y, 'z': scene.camera.center.z},
            'up': {'x': scene.camera.up.x, 'y': scene.camera.up.y, 'z': scene.camera.up.z}
        }
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Update the traces
        self.update_points()
        
        # Restore the view state
        self.model.figure.update_layout(
            scene_camera=self.original_view,
            uirevision="noreset"  # Changed from "lock" to "noreset"
        )
    
    def update_points(self):
        self.model.figure.update_traces(
            selector={"name": "Clicked Points"},
            x=self.model.points.x,
            y=self.model.points.y,
            z=self.model.points.z,
            marker={
                'color': self.model.points.marker.color,
                'size': self.model.points.marker.size
            }
        )