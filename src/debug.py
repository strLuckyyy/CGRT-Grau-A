# debug.py
'''
Overlays visuais de debug para volumes de bounding e níveis de LOD.

Dois modos independentes controlados por flags em DebugRenderer:

  show_bounding — AABB em wireframe branco ao redor de cada objeto,
                  refletindo exatamente o volume usado no frustum culling.

  show_lod      — Wireframe colorido indicando o LOD ativo de cada objeto:
                    VERDE   = HIGH
                    AMARELO = MEDIUM
                    VERMELHO= LOW
'''

import ctypes
import numpy as np
from OpenGL.GL import *
import OpenGL.GL.shaders

from lod import LOD


# ---- SHADERS ----

_VERT_SRC = """
#version 400
layout(location = 0) in vec3 pos;
uniform mat4 view;
uniform mat4 proj;
void main() {
    gl_Position = proj * view * vec4(pos, 1.0);
}
"""

_FRAG_SRC = """
#version 400
uniform vec3 line_color;
out vec4 frag_color;
void main() {
    frag_color = vec4(line_color, 1.0);
}
"""

_LOD_COLORS = {
    LOD.HIGH:   np.array([0.0, 1.0, 0.0], dtype=np.float32),
    LOD.MEDIUM: np.array([1.0, 1.0, 0.0], dtype=np.float32),
    LOD.LOW:    np.array([1.0, 0.0, 0.0], dtype=np.float32),
}
_BOUNDING_COLOR = np.array([1.0, 1.0, 1.0], dtype=np.float32)

# 12 arestas de um cubo unitário expressas como 24 índices de endpoints de linhas
_BOX_INDICES = np.array([
    0,1, 1,2, 2,3, 3,0,
    4,5, 5,6, 6,7, 7,4,
    0,4, 1,5, 2,6, 3,7,
], dtype=np.uint32)


def _box_vertices(world_min: np.ndarray, world_max: np.ndarray) -> np.ndarray:
    x0, y0, z0 = world_min
    x1, y1, z1 = world_max
    return np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1],
        [x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1],
    ], dtype=np.float32)


class DebugRenderer:
    '''
    Desenha overlays de AABB em wireframe usando um shader simples sem iluminação.
    Um único VAO é reutilizado a cada draw; os vértices são enviados via glBufferSubData.
    '''

    def __init__(self):
        self.show_bounding = False
        self.show_lod      = False

        self._program = self._compile_program()
        self._vao, self._vbo, self._ebo = self._build_buffers()

    # ---- SETUP ----

    def _compile_program(self) -> int:
        vs   = OpenGL.GL.shaders.compileShader(_VERT_SRC, GL_VERTEX_SHADER)
        fs   = OpenGL.GL.shaders.compileShader(_FRAG_SRC, GL_FRAGMENT_SHADER)
        prog = OpenGL.GL.shaders.compileProgram(vs, fs)
        glDeleteShader(vs)
        glDeleteShader(fs)
        return prog

    def _build_buffers(self):
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)

        glBindVertexArray(vao)

        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, 8 * 3 * 4, None, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, _BOX_INDICES.nbytes, _BOX_INDICES, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)
        return int(vao), int(vbo), int(ebo)

    # ---- DRAW ----

    def _set_uniform_mat4(self, name: str, mat: np.ndarray) -> None:
        glUniformMatrix4fv(glGetUniformLocation(self._program, name), 1, GL_TRUE, mat)

    def _set_uniform_vec3(self, name: str, v: np.ndarray) -> None:
        glUniform3f(glGetUniformLocation(self._program, name), v[0], v[1], v[2])

    def _draw_box(self, world_min: np.ndarray, world_max: np.ndarray, color: np.ndarray) -> None:
        verts = _box_vertices(world_min, world_max)
        self._set_uniform_vec3("line_color", color)
        glBindVertexArray(self._vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glDrawElements(GL_LINES, len(_BOX_INDICES), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def render(self, objects, camera, current_lods: dict) -> None:
        if not self.show_bounding and not self.show_lod:
            return

        glUseProgram(self._program)
        glDisable(GL_DEPTH_TEST)  # always draw on top so overlays are never hidden
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        aspect = camera.width / camera.height
        self._set_uniform_mat4("view", camera.view_matrix())
        self._set_uniform_mat4("proj", camera.projection_matrix(aspect))

        for obj in objects:
            world_min, world_max = obj.bounding_volume.get_world_aabb(obj.position)

            if self.show_bounding:
                self._draw_box(world_min, world_max, _BOUNDING_COLOR)

            if self.show_lod:
                lod    = current_lods.get(id(obj), LOD.HIGH)
                color  = _LOD_COLORS[lod]
                margin = np.array([0.15, 0.15, 0.15], dtype=np.float32)
                self._draw_box(world_min - margin, world_max + margin, color)

        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
