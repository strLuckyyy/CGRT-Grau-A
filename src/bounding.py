# bounding.py
import numpy as np


class BoundingType:
    SPHERE = 0
    AABB   = 1


class Bounding:
    '''
    Caixa delimitadora alinhada aos eixos (AABB) ou esfera delimitadora em espaço local do objeto.

    Após a construção, o volume está no espaço local. Chame bake_transform()
    uma vez (via Object.__init__) para pré-computar os limites em espaço de mundo usando
    a escala e rotação do objeto. Os testes de frustum então precisam apenas da
    posição em mundo do objeto, mantendo o custo por frame em apenas um produto escalar por plano.
    '''

    def __init__(self, type, center, radius=None, min=None, max=None, vertex=None):
        self.type   = type
        self.center = np.zeros(3, dtype=np.float32)
        self.radius = radius
        self.min    = min
        self.max    = max

        if vertex is not None:
            self._build(vertex)

        self._scaled_center    = self.center.copy()
        self._scaled_extension = None
        self._scaled_radius    = radius

    # ---- BUILD ----

    def _build(self, vertex) -> None:
        if self.type == BoundingType.SPHERE:
            self.center = np.mean(vertex, axis=0).astype(np.float32)
            self.radius = float(np.max(np.linalg.norm(vertex - self.center, axis=1)))

        elif self.type == BoundingType.AABB:
            self.min    = np.min(vertex, axis=0).astype(np.float32)
            self.max    = np.max(vertex, axis=0).astype(np.float32)
            self.center = ((self.min + self.max) / 2).astype(np.float32)

    # ---- BAKE ----

    def bake_transform(self, scale: np.ndarray, rot_matrix: np.ndarray) -> None:
        '''
        Pré-computa o deslocamento do centro e a extensão em espaço de mundo dado escala e rotação.
        Deve ser chamado uma vez após a matriz de transformação do objeto estar definida.

        Para AABB, os semi-extents rotacionados são projetados em cada eixo do mundo usando
        |R| para que a AABB resultante continue alinhada aos eixos e sempre contenha a OBB.
        '''
        s = np.asarray(scale, dtype=np.float32)
        R = np.asarray(rot_matrix, dtype=np.float32)

        self._scaled_center = (R @ (self.center * s)).astype(np.float32)

        if self.type == BoundingType.SPHERE:
            self._scaled_radius    = float(self.radius * np.max(s))
            self._scaled_extension = None

        elif self.type == BoundingType.AABB:
            half_local = ((self.max - self.min) / 2) * s
            # |R| projects each half-extent onto all world axes conservatively
            self._scaled_extension = (np.abs(R) @ half_local).astype(np.float32)
            self._scaled_radius    = None

    def bake_scale(self, scale: np.ndarray) -> None:
        self.bake_transform(scale, np.identity(3, dtype=np.float32))

    # ---- FRUSTUM ----

    def is_on_frustum(self, planes, world_position) -> bool:
        world_center = world_position + self._scaled_center

        if self.type == BoundingType.SPHERE:
            r = self._scaled_radius
            for (normal, d) in planes:
                if np.dot(normal, world_center) + d < -r:
                    return False

        elif self.type == BoundingType.AABB:
            ext = self._scaled_extension
            for (normal, d) in planes:
                if np.dot(normal, world_center) + d < -np.dot(np.abs(normal), ext):
                    return False

        return True

    def is_on_bad_frustum(self, planes, world_position) -> bool:
        '''
        Teste de frustum intencionalmente incorreto: adiciona uma margem fixa que faz com que
        objetos bem fora do frustum ainda passem no teste, simulando uma implementação
        mal ajustada de culling que nunca descarta geometria suficiente.
        '''
        world_center = world_position + self._scaled_center
        MARGIN = 8.0

        if self.type == BoundingType.SPHERE:
            r = self._scaled_radius
            for (normal, d) in planes:
                if np.dot(normal, world_center) + d < -r - MARGIN:
                    return False

        elif self.type == BoundingType.AABB:
            ext = self._scaled_extension
            for (normal, d) in planes:
                if np.dot(normal, world_center) + d < -np.dot(np.abs(normal), ext) + MARGIN:
                    return False

        return True

    # ---- WORLD AABB ----

    def get_world_aabb(self, world_position) -> tuple[np.ndarray, np.ndarray]:
        if self.type == BoundingType.AABB and self._scaled_extension is not None:
            c   = world_position + self._scaled_center
            ext = self._scaled_extension
            return c - ext, c + ext

        elif self.type == BoundingType.SPHERE:
            r = self._scaled_radius or 0.0
            c = world_position + self._scaled_center
            return c - r, c + r

        return world_position.copy(), world_position.copy()
