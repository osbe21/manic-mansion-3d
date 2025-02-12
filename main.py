from renderer import *
from object3d import *


class Game(Renderer):
    def init(self):
        self.player = Player(speed=0.5, rotation_speed=50)

        self.camera = self.player

        self.ground = Mesh(position=[0, -1, 0], path="models/ground.obj", render_behind=True)

        self.ghost = Mesh(path="models/ghost.obj")
        self.sheep = Mesh(path="models/sheep.obj", position=[0.7, -.3, -1.5], scale=[.3, .3, .3])

        self.ghost.position[2] -= 1.5
        self.ghost.position[1] -= .3
        self.ghost.scale *= .2

        self.add_mesh(self.ground, self.ghost, self.sheep)

    def update(self):
        self.ghost.rotation[1] += 20 * self.deltaTime

        self.player.update_position(self.deltaTime)
        self.player.update_rotation(self.deltaTime)
    

Game(800, 600, light_dir=[.3, -1, -.3], window_caption="Manic Mansion 3D")