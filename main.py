from renderer import *
from object3d import *
from random import random

class Game(Renderer):
    def init(self):
        self.bg_color = (139, 203, 252)

        self.player = Player(speed=0.5, rotation_speed=50, position=[0, 0, 5])

        self.camera = self.player

        self.trees = []

        self.ground = Mesh(position=[0, -1, 0], path="models/ground.obj", render_behind=True)

        self.ghost = Mesh(path="models/ghost.obj", position=[0, -.3, -1.5], scale=[.2]*3)
        self.sheep = Mesh(path="models/sheep.obj", position=[0.7, -.3, -1.5], scale=[.3]*3)

        self.instantiate_trees(5)

        self.add_mesh(self.ghost, self.sheep)
        self.add_mesh(self.ground)


    def update(self):
        # self.ghost.rotation[1] += 20 * self.deltaTime

        self.player.update_position(self.deltaTime)
        self.player.update_rotation(self.deltaTime)
    

    def instantiate_trees(self, num_trees):
        for i in range(num_trees):
            position = [(random() - 0.5) * 8, -1, (random() - 0.5) * 8]
            rotation = [0, i * 360 / num_trees, 0]#[0, random() * 360, 0]
            scale = [.8] * 3

            tree = Mesh(position=position, rotation=rotation, scale=scale, path="models/tree.obj")

            self.trees.append(tree)

        self.add_mesh(*self.trees)
    

Game(1200, 675, light_dir=[.3, -1, -.3], window_caption="Manic Mansion 3D")