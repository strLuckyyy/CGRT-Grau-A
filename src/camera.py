# camera.py
import numpy as np
from numpy.typing import NDArray


class Camera:
    '''
    Câmera em primeira pessoa com controle de yaw/pitch.

    Fornece matriz de visão, matriz de projeção e extração dos planos do frustum.
    Todas as matrizes são construídas sob demanda; não há cache porque a câmera
    se move a cada frame e o custo é desprezível comparado aos draw calls.
    '''

    def __init__(
        self,
        width:    int   = 1280,
        height:   int   = 720,
        position: NDArray[np.float32] | None = None,
        yaw:      float = -90.0,
        pitch:    float =   0.0,
        fov:      float =  67.0,
        near:     float =   0.1,
        far:      float = 200.0,
        speed:    float =  15.0
    ):
        self.width    = width
        self.height   = height
        self.position = np.array([0.0, 2.0, 8.0] if position is None else position, dtype=np.float32)
        self.yaw      = yaw
        self.pitch    = pitch
        self.fov      = fov
        self.near     = near
        self.far      = far
        self.speed    = speed

        self.up          = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.first_mouse = True
        self.last_x      = width  / 2
        self.last_y      = height / 2

    # ---- MATRICES ----

    def view_matrix(self) -> NDArray[np.float32]:
        front = self._calc_front()
        s = np.cross(front, self.up);  s /= np.linalg.norm(s)
        u = np.cross(s, front)

        view = np.identity(4, dtype=np.float32)
        view[0, :3] =  s;     view[0, 3] = -np.dot(s,     self.position)
        view[1, :3] =  u;     view[1, 3] = -np.dot(u,     self.position)
        view[2, :3] = -front; view[2, 3] =  np.dot(front, self.position)

        return view

    def projection_matrix(self, aspect: float) -> NDArray[np.float32]:
        fov = np.radians(self.fov)
        a   = 1.0 / (np.tan(fov / 2.0) * aspect)
        b   = 1.0 /  np.tan(fov / 2.0)
        c   = (self.far + self.near) / (self.near - self.far)
        d   = (2.0 * self.near * self.far) / (self.near - self.far)

        return np.array([
            [a,   0.0, 0.0,  0.0],
            [0.0, b,   0.0,  0.0],
            [0.0, 0.0, c,    d  ],
            [0.0, 0.0, -1.0, 0.0],
        ], dtype=np.float32)

    # ---- FRUSTUM ----

    def extract_frustum_planes(self, aspect: float) -> list:
        front = self._calc_front()
        right = np.cross(front, self.up);  right /= np.linalg.norm(right)
        up    = np.cross(right, front)

        tang       = np.tan(np.radians(self.fov) / 2.0)
        half_h_far = self.far * tang
        half_w_far = half_h_far * aspect

        def plane(normal, point):
            n = normal / np.linalg.norm(normal)
            return (n, -np.dot(n, point))

        return [
            ( front.copy(), -np.dot(front, self.position + front * self.near)),
            (-front.copy(),  np.dot(front, self.position + front * self.far )),
            plane(np.cross(front * self.far - right * half_w_far,  up),   self.position),
            plane(np.cross(up,    front * self.far + right * half_w_far),  self.position),
            plane(np.cross(right, front * self.far - up    * half_h_far),  self.position),
            plane(np.cross(front * self.far + up * half_h_far, right),     self.position),
        ]

    # ---- HELPERS ----

    def _calc_front(self) -> NDArray[np.float32]:
        front = np.array([
            np.cos(np.radians(self.yaw))   * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw))   * np.cos(np.radians(self.pitch)),
        ], dtype=np.float32)
        return front / np.linalg.norm(front)

    def update_window_size(self, width: int, height: int) -> None:
        self.width  = width
        self.height = height
