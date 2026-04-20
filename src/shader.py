# shader.py
import numpy as np
import OpenGL.GL.shaders
from OpenGL.GL import *


class Shader:
    '''Compila um programa GLSL a partir de arquivos de vertex e fragment shader e expõe setters tipados para uniforms.'''

    def __init__(
        self,
        vert_path: str = "./shader/vertex.glsl",
        frag_path: str = "./shader/fragment.glsl"
    ) -> None:
        def _src(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()

        vs = OpenGL.GL.shaders.compileShader(_src(vert_path), GL_VERTEX_SHADER)
        fs = OpenGL.GL.shaders.compileShader(_src(frag_path), GL_FRAGMENT_SHADER)
        self.program: int = OpenGL.GL.shaders.compileProgram(vs, fs)
        glDeleteShader(vs)
        glDeleteShader(fs)

    def use(self) -> None:
        glUseProgram(self.program)

    # ---- UNIFORM SETTERS ----

    def set_mat4(self, name: str, matrix: np.ndarray) -> None:
        glUniformMatrix4fv(glGetUniformLocation(self.program, name), 1, GL_TRUE, matrix)

    def set_vec4(self, name: str, v: np.ndarray) -> None:
        glUniform4f(glGetUniformLocation(self.program, name), v[0], v[1], v[2], v[3])

    def set_int(self, name: str, value: int) -> None:
        glUniform1i(glGetUniformLocation(self.program, name), value)
