from typing import Optional

from Model import Model
from InteractiveModel import InteractiveModel
from TextureMapper import TextureMapper

class SceneBuilder:
    def __init__(
        self,
        model_path: str = './assets/lego_man.glb',
        texture_path: Optional[str] = None
    ):
        self.model = Model(model_path)
        self.texture_mapper = TextureMapper(texture_path) if texture_path else None
        
        # Apply texture before making it interactive 
        if self.texture_mapper:
            self.texture_mapper.apply_texture(self.model)

        self.interactive_model = InteractiveModel(self.model)

