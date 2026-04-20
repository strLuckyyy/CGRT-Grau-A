# object.py
import enum
import numpy as np
import bounding as bd
from loader import load_obj
from lod import LOD


class ObjectType(enum.Enum):
    BUILDING = 1
    CACTUS   = 2
    CART     = 3
    PROP     = 4
    LANTERN  = 5
    GROUND   = 6


class Object:
    '''
    Representa uma entidade renderizável da cena com malhas em LOD, volume de bounding,
    e uma única matriz de modelo 4x4 que codifica translação, rotação e escala.

    O volume de bounding é pré-processado (baked) uma vez a partir da matriz de modelo
    no momento da construção e nunca é recalculado, evitando custo por frame.
    '''

    def __init__(
        self,
        lod_files:      dict       = {LOD.HIGH.value: None},
        color:          tuple      = (1.0, 1.0, 1.0, 1.0),
        bound_type:     int        = bd.BoundingType.AABB,
        may_be_batched: bool       = False,
        object_type:    ObjectType = ObjectType.BUILDING,
        transform:      np.ndarray = None,
    ):
        self.color       = np.array(color, dtype=np.float32)
        self.object_type = object_type
        self.may_be_batched = may_be_batched
        self.current_lod    = LOD.HIGH

        # Armazena a matriz de modelo completa; a posição é sua última coluna
        self._transform = transform if transform is not None else np.identity(4, dtype=np.float32)

        self.meshes = {
            LOD.HIGH:   load_obj(lod_files[LOD.HIGH.value])   if lod_files.get(LOD.HIGH.value)   else None,
            LOD.MEDIUM: load_obj(lod_files[LOD.MEDIUM.value]) if lod_files.get(LOD.MEDIUM.value) else None,
            LOD.LOW:    load_obj(lod_files[LOD.LOW.value])    if lod_files.get(LOD.LOW.value)    else None,
        }

        high_mesh = self.meshes[LOD.HIGH]
        positions = high_mesh.positions if high_mesh else np.zeros((1, 3), dtype=np.float32)
        self.bounding_volume = bd.Bounding(bound_type, center=np.zeros(3), vertex=positions)

        # Decompõe a matriz uma vez para que o bounding possa ser pré-processado
        # sem precisar rodar uma SVD completa a cada frame — os vetores coluna já dão a escala por eixo.
        self._bake_bounding()

    # ---- BOUNDING ----

    def _bake_bounding(self) -> None:
        '''
        Extrai escala e rotação da matriz de modelo armazenada e aplica
        ao volume de bounding. Chamado uma vez na construção; nunca mais.
        '''
        M = self._transform
        # Comprimento das colunas da submatriz 3x3 superior-esquerda são os fatores de escala por eixo.
        sx = float(np.linalg.norm(M[:3, 0]))
        sy = float(np.linalg.norm(M[:3, 1]))
        sz = float(np.linalg.norm(M[:3, 2]))
        scale = np.array([sx, sy, sz], dtype=np.float32)

        # Normalizar as colunas resulta na matriz de rotação pura.
        R = M[:3, :3] / np.array([sx, sy, sz], dtype=np.float32)
        self.bounding_volume.bake_transform(scale, R)

    # ---- TRANSFORM ----

    @property
    def position(self) -> np.ndarray:
        return self._transform[:3, 3].copy()

    def get_transform(self) -> np.ndarray:
        return self._transform

    # ---- MESH GETTERS ----

    def get_mesh_data(self, lod: LOD):
        return self.meshes.get(lod)

    def get_vao(self, lod: LOD) -> int | None:
        mesh = self.meshes.get(lod)
        return mesh.vao if mesh else None

    def get_index_count(self, lod: LOD) -> int:
        mesh = self.meshes.get(lod)
        return mesh.index_count if mesh else 0

    def get_triangle_count(self, lod: LOD) -> int:
        return self.get_index_count(lod) // 3