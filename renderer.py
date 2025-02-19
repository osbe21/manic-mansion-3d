import pygame
import numpy as np
from object3d import *
from config import *


class Renderer:
    def __init__(self, width, height, fov=60, bg_color=(80, 80, 80), light_dir=[0, -1, 0], fps=60, window_caption=""):
        # Init pygame
        pygame.init()
        pygame.display.set_caption(window_caption)
        pygame.mouse.set_visible(False)

        self.SCREEN_SIZE = (width, height)

        self.screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Calibri', 40)
        self.bg_color : tuple[int] = bg_color
        self.mesh_list : list[Mesh] = []
        self.camera = Object3D()
        self.deltaTime = 1/fps
        self.running = True
        self.light_dir = np.array([*light_dir, 0], dtype=DTYPE)
        self.light_dir /= np.linalg.norm(light_dir)


        aspect = width / height
        f = 1 / np.tan(np.radians(fov) / 2)
        far = 100
        near = 0.01
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
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            
            self.screen.fill(self.bg_color)

            self.render()

            self.update()

            self.blit_fps()

            pygame.display.flip()

            self.deltaTime = self.clock.tick(fps) / 1000

    
    def render(self):
        view_matrix = np.linalg.inv(self.camera.transformation_matrix)
        view_projection_matrix = self.projection_matrix @ view_matrix

        sorted_mesh_list = sorted(self.mesh_list,
                                  key=lambda mesh: 9999 if mesh.render_behind else np.linalg.norm(mesh.position - self.camera.position),
                                  reverse=True)

        for mesh in sorted_mesh_list:
            transformed_vertices = mesh.vertices_4d.copy()

            mvp_matrix = view_projection_matrix @ mesh.transformation_matrix

            # Transformer til clip space
            transformed_vertices @= mvp_matrix.T

            # Del på w (ekte clip space)
            transformed_vertices /= transformed_vertices[:, 3:4]
            
            # Lag en mask for å culle alle faces som er delvis eller helt ute av NDC
            # TODO?: clip alle faces utenfor NDC
            faces_ndc = transformed_vertices[mesh.faces]
            
            inside_ndc_mask = np.all(
                (faces_ndc[:, :, 0] >= -1) & (faces_ndc[:, :, 0] <= 1) &
                (faces_ndc[:, :, 1] >= -1) & (faces_ndc[:, :, 1] <= 1) &
                (faces_ndc[:, :, 2] >= -1) & (faces_ndc[:, :, 2] <= 1),
                axis=1
            )

            # Få normaler i view space
            # transformed_normals = mesh.face_normals @ (view_matrix @ mesh.transformation_matrix).T

            # frontface_mask = transformed_normals[:, 2] < 0

            # Mask for frontface normaler og faces innenfor ndc
            face_mask = inside_ndc_mask #& frontface_mask

            filtered_faces = transformed_vertices[mesh.faces[face_mask]]

            # Sorterer alle faces, painters algorithm
            # TODO?: Lag bybdebuffer?
            z_values = filtered_faces[:, :, 2]
            avg_z = z_values.mean(axis=1)
            
            sorted_face_indeces = np.argsort(avg_z)[::-1]

            # Gjør om fra clip space til screen space
            transformed_vertices[:, 0] += 1
            transformed_vertices[:, 0] *= (self.SCREEN_SIZE[0] / 2)

            transformed_vertices[:, 1] = 1 - transformed_vertices[:, 1]
            transformed_vertices[:, 1] *= (self.SCREEN_SIZE[1] / 2)

            # Precompute lambert verdier
            transformed_normals = mesh.face_normals[face_mask] @ mesh.rotation_matrix.T
            lambert_values = np.clip(np.dot(transformed_normals, self.light_dir), .1, 1)

            tris = transformed_vertices[mesh.faces[face_mask]][:, :, :2]

            for face_index in sorted_face_indeces:
                tri = tris[face_index]

                diffuse = mesh.diffuse * lambert_values[face_index]

                pygame.draw.polygon(self.screen, diffuse, tri)
    
    def blit_fps(self):
        fps_text = self.font.render(f"FPS: {self.clock.get_fps():.0f}", 1, (0, 0, 0))
        self.screen.blit(fps_text, (20, 20))

    def add_mesh(self, *args):
        self.mesh_list.extend(args)

    def init(self):
        pass

    def update(self):
        pass