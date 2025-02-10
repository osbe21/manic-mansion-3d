import numpy as np
import pywavefront
from transformations import *
from config import *

FORWARD = np.array([0, 0, -1, 1])

class Object3D:
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1]):
        self.position = np.array(position, dtype=DTYPE)
        self.rotation = np.array(rotation, dtype=DTYPE)
        self.scale = np.array(scale, dtype=DTYPE)

    @property
    def forward(self):
        return np.dot(FORWARD, self.rotation_matrix)[:3]

    @property
    def translation_matrix(self):
        return translation_matrix(self.position)
    
    @property
    def rotation_matrix(self):
        return z_rotation_matrix(self.rotation[2]) @ y_rotation_matrix(self.rotation[1]) @ x_rotation_matrix(self.rotation[0])

    @property
    def scaling_matrix(self):
        return scaling_matrix(self.scale)
    
    @property
    def transformation_mat(self):
        return self.translation_matrix @ self.rotation_matrix @ self.scaling_matrix


class Mesh(Object3D):
    def __init__(self, vertices=[], faces=[], path="", load_from_file=False, color=(255, 255, 255), *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._vertices : np.ndarray = None
        self._vertices_4d : np.ndarray = None
        self._faces : np.ndarray = np.array(faces)
        self._face_normals : np.ndarray = None

        self.diffuse = np.array(color)

        if load_from_file:
            self.load_from_obj(path)
        else:
            self.vertices = vertices

    @property
    def vertices(self):
        return self._vertices
    
    @property
    def vertices_4d(self):
        return self._vertices_4d

    @vertices.setter
    def vertices(self, value):
        self._vertices = np.array(value, dtype=DTYPE)

        if len(value) == 0:
            self._vertices_4d = np.array([], dtype=DTYPE)
            return

        n = self._vertices.shape[0]
        vertices4 = np.empty((n, 4), dtype=DTYPE)
        vertices4[:, :3] = self._vertices
        vertices4[:, 3] = 1 
        self._vertices_4d = vertices4
    
    @property
    def faces(self):
        return self._faces

    @faces.setter
    def faces(self, value):
        self._faces = np.array(value)
        
        normals = []

        for face in self._faces:
            triangle = self._vertices[face]

            tangent_1 = triangle[0, :3] - triangle[1, :3]
            tangent_2 = triangle[2, :3] - triangle[1, :3]

            normal = np.cross(tangent_1, tangent_2)
            normal /= np.linalg.norm(normal)
            
            normals.append(np.array([*normal, 1]))
        
        self._face_normals = np.array(normals)


    @property
    def face_normals(self):
        return self._face_normals
    
    def load_from_obj(self, path):
        scene = pywavefront.Wavefront(path, collect_faces=True, create_materials=True)

        faces = []
        
        for mesh in scene.mesh_list:
            faces.extend(mesh.faces)
        
        diffuse = list(scene.materials.values())[0].diffuse

        self.vertices = scene.vertices
        self.faces = faces
        self.diffuse = np.array(diffuse) * 255
