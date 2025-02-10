import pygame
import numpy as np
from object3d import *
from config import *
    

class Renderer:
    def __init__(self, width, height, fov=60, bg_color=(80, 80, 80), light_dir=[0, -1, 0], fps=60, window_caption=""):
        # Init pygame
        pygame.init()
        pygame.display.set_caption(window_caption)

        self.SCREEN_SIZE = (width, height)

        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Consolas', 30)
        self.bg_color : tuple[int] = bg_color
        self.mesh_list : list[Mesh] = []
        self.camera = Object3D()
        self.deltaTime = 1/fps
        self.running = True
        self.light_dir = np.array(light_dir, dtype=DTYPE)
        self.light_dir /= np.linalg.norm(light_dir)


        aspect = width / height
        f = 1 / np.tan(np.radians(fov) / 2)
        far = 1000
        near = 0.1
        nf = 1 / (near - far)

        self.projection_matrix = np.array([
            [f / aspect, 0,  0,  0],
            [0,  f,  0,  0],
            [0,  0, (far + near) * nf, (2 * far * near) * nf],
            [0,  0, -1,  0]
        ], dtype=DTYPE)


        self.init()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()
            
            self.screen.fill(self.bg_color)

            self.render()

            fps_text = self.font.render(f"FPS: {1/self.deltaTime:.0f}", 1, (0, 0, 0))
            self.screen.blit(fps_text, (20, 20))

            pygame.display.flip()

            self.deltaTime = self.clock.tick(fps) / 1000

    
    def render(self):
        view_projection_matrix = self.projection_matrix @ np.linalg.inv(self.camera.transformation_mat)
        camera_forward = self.camera.forward

        for mesh in self.mesh_list:
            transformed_vertices = mesh.vertices_4d.copy()
            transformed_normals = mesh.face_normals.copy()

            mvp_matrix = view_projection_matrix @ mesh.transformation_mat

            # Transformer til clip space
            transformed_vertices @= mvp_matrix.T

            # Del på w
            transformed_vertices[:] = transformed_vertices / transformed_vertices[:, 3:4]

            # Gjør om fra clip space til screen space
            transformed_vertices[:, 0] += 1
            transformed_vertices[:, 0] *= (self.SCREEN_SIZE[0] / 2)

            transformed_vertices[:, 1] = 1 - transformed_vertices[:, 1]
            transformed_vertices[:, 1] *= (self.SCREEN_SIZE[1] / 2)

            # Transformer face normalene
            transformed_normals @= mesh.rotation_matrix.T

            # Filtrer ut faces utenfor NDC
            # TODO: sriv om til å clippe alle faces utenfor NDC
            z_values = transformed_vertices[mesh.faces][:, :, 2]
            avg_z = z_values.mean(axis=1)
            
            valid_mask = avg_z <= 1

            avg_z = avg_z[valid_mask]
            filtered_faces = mesh.faces[valid_mask]
            filtered_face_normals = transformed_normals[valid_mask]
            
            sorted_face_indeces = np.argsort(avg_z)[::-1]

            for face_index in sorted_face_indeces:
                face_normal = filtered_face_normals[face_index, :3]

                # Backface culling
                if np.dot(face_normal, camera_forward) <= 0:
                    continue

                face = filtered_faces[face_index]
                triangle = np.array([transformed_vertices[idx] for idx in face])

                lambert = np.dot(face_normal, self.light_dir)
                lambert = max(lambert, 0.1)

                diffuse = mesh.diffuse * lambert

                pygame.draw.polygon(self.screen, diffuse, triangle[:, :2])


    def add_mesh(self, mesh):
        self.mesh_list.append(mesh)

    def init(self):
        pass

    def update(self):
        pass


class Game(Renderer):
    def init(self):
        self.mesh = Mesh(path="models/stanford.obj", load_from_file=True)

        self.mesh.scale *= 15
        self.mesh.position[2] -= 1.5
        self.mesh.position[1] -= .3
        self.mesh.scale *= .2

        self.add_mesh(self.mesh)

    def update(self):
        self.mesh.rotation[1] += 30 * self.deltaTime
    

Game(800, 600, light_dir=[.3, -1, .1], window_caption="Sauespill")