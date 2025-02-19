from renderer import *
from object3d import *
from random import random
import math


class Game(Renderer):
    def init(self):
        self.bg_color = (139, 203, 252)

        self.WORLD_BOUNDS = {"x": 4.5, "z": -18*1.5}

        self.player = Player(speed=3, rotation_speed=80, position=[0, .8, 0])
        self.camera = self.player

        self.pick_up_text = self.font.render("Press 'E' to pick up", True, (255, 255, 255), (0, 0, 0))
        self.drop_text = self.font.render("Press 'Q' to drop", True, (255, 255, 255), (0, 0, 0))

        self.ground_height = -.8
        ground = Mesh(path="models/ground.obj", position=[0, self.ground_height, 0], scale=[1, 1, 1.5], render_behind=True)
        fence = Mesh(path="models/fence.obj", position=[0, self.ground_height, 0], scale=[1, 1, 1.5], render_behind=True)
        self.add_mesh(ground, fence)

        self.trees = []
        self.instantiate_trees(15)

        self.sheep = []
        self.instantiate_sheep()

        self.ghosts = []
        self.ghost_offsets = []
        self.instantiate_single_ghost()

        self.jumping_sheep = []

        self.carried_sheep = None
        self.score = 0


    def update(self):
        self.player.update_position(self.deltaTime)
        self.player.update_rotation(self.deltaTime)

        self.detect_fence_collision()
        self.detect_tree_collisions(2)
        self.detect_ghost_collision(1.3)

        self.update_ghosts()
        self.update_sheep_jump()
        self.update_carried_sheep()
        self.sheep_interctions(2.5)
        
        self.print_score()


    def instantiate_trees(self, num_trees):
        while len(self.trees) < num_trees:
            x = (random() * 2 - 1) * (self.WORLD_BOUNDS["x"] - 1)
            z = random() * (self.WORLD_BOUNDS["z"] + 6) - 3
            position = np.array([x, self.ground_height, z])
            rotation = [0, random() * 360, 0]

            # Ineffektivt, burde bruke disc sampling, men er for lat
            discard = False
            for tree in self.trees:
                if np.linalg.norm(tree.position - position) < 2:
                    discard = True
                    break

            if discard:
                continue

            tree = Mesh(position=position, rotation=rotation, scale=[1.2]*3, path="models/tree.obj")

            self.trees.append(tree)

        self.add_mesh(*self.trees)


    def instantiate_single_sheep(self):
        x = (random() * 2 - 1) * (self.WORLD_BOUNDS["x"] - 1)
        z = -random() * 3 + self.WORLD_BOUNDS["z"] + 3
        position = [x, self.ground_height, z]
        rotation = [0, random() * 360, 0]

        sheep = Mesh(path="models/sheep.obj", position=position, rotation=rotation)

        self.sheep.append(sheep)
        self.add_mesh(sheep)


    def instantiate_sheep(self):
        for i in range(3):
            self.instantiate_single_sheep()
    

    def instantiate_single_ghost(self):
        position = [0, 0, self.WORLD_BOUNDS["z"]/2]
        rotation = [0, random() * 360, 0]

        ghost = Mesh(path="models/ghost_lp.obj", position=position, rotation=rotation, scale=[.7]*3)

        self.ghosts.append(ghost)
        self.ghost_offsets.append(random())
        self.add_mesh(ghost)

    
    def update_ghosts(self):
        for ghost, offset in zip(self.ghosts, self.ghost_offsets):
            ghost.position += -ghost.forward * 2 * self.deltaTime
            ghost.position[1] = math.sin(pygame.time.get_ticks()/200 + offset) * .1
            
            if self.WORLD_BOUNDS["x"] < ghost.position[0] or ghost.position[0] < -self.WORLD_BOUNDS["x"]:
                ghost.rotation[1] *= -1
                ghost.position += -ghost.forward * 2 * self.deltaTime
            
            if self.WORLD_BOUNDS["z"] + 4 > ghost.position[2] or ghost.position[2] > -4:
                ghost.rotation[1] = 180 - ghost.rotation[1]
                ghost.position += -ghost.forward * 2 * self.deltaTime


    def detect_ghost_collision(self, collision_dist):
        for ghost in self.ghosts:
            dist = np.linalg.norm(ghost.position - self.player.position)

            if dist < collision_dist:
                self.running = False
                print('\033[91m' + "Din Score Ble: " + str(self.score) + '\033[0m')


    def detect_fence_collision(self):
        x_bounds = self.WORLD_BOUNDS["x"]
        x_pos = self.player.position[0]
        self.player.position[0] = max(-x_bounds, min(x_bounds, x_pos))
        
        z_bounds = self.WORLD_BOUNDS["z"]
        z_pos = self.player.position[2]
        self.player.position[2] = min(0, max(z_bounds, z_pos))


    def print_score(self):
        text = self.font.render(f"Score: {self.score}", True, (255, 255, 255), (0, 0, 0))
        self.screen.blit(text, (self.SCREEN_SIZE[0] - 200, 20))


    def update_sheep_jump(self):
        for sheep, offset in self.jumping_sheep:
            time = pygame.time.get_ticks()/1000
            value = abs(math.sin((time + offset) * 6)) * .4
            sheep.position[1] = self.ground_height + value

            sheep.rotation[1] += 50 * self.deltaTime


    def update_carried_sheep(self):
        if not self.carried_sheep: return
        
        self.carried_sheep.position = self.player.position + self.player.forward
        self.carried_sheep.position[1] = -.7
        self.carried_sheep.rotation = [0, self.player.rotation[1] + 90, 0]


    def sheep_interctions(self, interaction_dist):
        keys = pygame.key.get_pressed()

        if self.carried_sheep:
            if self.player.position[2] >= -3: # Hvis spilleren er i sonen hvor de kan slippe sauen
                rect = self.drop_text.get_rect(center=(self.SCREEN_SIZE[0]/2, self.SCREEN_SIZE[1]/2))
                self.screen.blit(self.drop_text, rect)

                if keys[pygame.K_q]:
                    self.player.speed = 3
                    self.score += 1
                    self.jumping_sheep.append((self.carried_sheep, random()))
                    self.carried_sheep.position = self.player.position + self.player.forward * 1.2
                    self.carried_sheep.position[1] = self.ground_height
                    self.carried_sheep = None
                    self.instantiate_single_sheep()
                    self.instantiate_single_ghost()
        else:
            for sheep in self.sheep:
                dist = np.linalg.norm(self.player.position - sheep.position)

                if dist < interaction_dist:
                    rect = self.pick_up_text.get_rect(center=(self.SCREEN_SIZE[0]/2, self.SCREEN_SIZE[1]/2))
                    self.screen.blit(self.pick_up_text, rect)

                    if keys[pygame.K_e]:
                        self.player.speed = 2
                        self.carried_sheep = sheep
                        self.sheep.remove(sheep)

    
    def detect_tree_collisions(self, collision_dist):
        for tree in self.trees:
            vec = self.player.position - tree.position
            dist = np.linalg.norm(vec)

            if dist < collision_dist:
                vec /= dist # normaliser
                vec[1] = 0
                self.player.position += vec * (collision_dist - dist)


Game(1400, 700, light_dir=[-.5, -1, 0], window_caption="Manic Mansion 3D")