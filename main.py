from renderer import *
from object3d import *


class Game(Renderer):
    def init(self):
        self.player = Player(speed=0.5, rotation_speed=50)

        self.camera = self.player

        self.ghost = Mesh(path="models/ghost.obj", load_from_file=True)
        self.sheep = Mesh(path="models/sheep.obj", load_from_file=True, position=[0.7, -.3, -1.5], scale=[.3, .3, .3])

        self.ghost.position[2] -= 1.5
        self.ghost.position[1] -= .3
        self.ghost.scale *= .2

        self.add_mesh(self.ghost)
        self.add_mesh(self.sheep)

    def update(self):
        self.ghost.rotation[1] += 20 * self.deltaTime

        self.player.update_position(self.deltaTime)
        self.player.update_rotation(self.deltaTime)
    

Game(800, 600, light_dir=[.3, -1, -.3], window_caption="Manic Mansion 3D")