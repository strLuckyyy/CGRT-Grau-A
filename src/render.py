# render.py
import numpy as np
from OpenGL.GL import *

from object import Object
from shader import Shader
from camera import Camera
from batching import build_static_batches, build_bad_batch
from lod import LOD, select_lod, select_bad_lod


_IDENTITY = np.identity(4, dtype=np.float32)


class Renderer:
    '''
    Responsável por todas as draw calls de um frame da cena.

    Suporta três caminhos de renderização (controlados por flags):
      - Padrão: uma draw call indexada por objeto.
      - Batching: uma draw call por grupo (ObjectType, LOD).
      - Batching ruim: uma draw call para tudo, sem granularidade de LOD ou culling.

    A seleção de LOD e o frustum culling são opções independentes que se aplicam
    aos caminhos padrão e batching; as versões ruins de cada um também podem ser
    ativadas separadamente para fins de comparação.
    '''

    def __init__(self):
        self.is_lod_enabled             = False
        self.is_frustum_culling_enabled = False
        self.is_batching_enabled        = False

        self.is_bad_lod_enabled             = False
        self.is_bad_frustum_culling_enabled = False
        self.is_bad_batching_enabled        = False

        self._static_batches: dict  = {}
        self._bad_batch:      tuple = (None, 0)

        self.draw_calls    = 0
        self.num_triangles = 0
        self.current_lods: dict = {}

    def init_batches(self, objects: list) -> None:
        '''Chamado uma vez após a criação da cena para construir os buffers de batch na GPU.'''
        self._static_batches = build_static_batches(objects)
        self._bad_batch      = build_bad_batch(objects)

    # ---- LOD ----

    def _pick_lod(self, camera: Camera, obj) -> LOD:
        if self.is_bad_lod_enabled: return select_bad_lod(camera, obj)
        if self.is_lod_enabled:     return select_lod(camera, obj)
        return LOD.HIGH

    def _compute_lods(self, objects: list, camera: Camera) -> None:
        self.current_lods = {id(obj): self._pick_lod(camera, obj) for obj in objects}

    # ---- FRUSTUM ----

    def _is_visible(self, obj, planes: list) -> bool:
        if self.is_frustum_culling_enabled:     return obj.bounding_volume.is_on_frustum(planes, obj.position)
        if self.is_bad_frustum_culling_enabled: return obj.bounding_volume.is_on_bad_frustum(planes, obj.position)
        return True

    # ---- BATCHING ----

    def _draw_static_batches(self, objects: list, shader: Shader) -> None:
        shader.set_int("use_vertex_color", 1)
        shader.set_mat4("transform", _IDENTITY)

        # Coleta apenas as chaves (tipo, lod) que estão realmente ativas neste frame
        active_keys: set = {
            (obj.object_type, self.current_lods[id(obj)])
            for obj in objects if obj.may_be_batched
        }

        for key in active_keys:
            batch = self._static_batches.get(key)
            if batch is None:
                continue
            vao, count = batch
            if vao and count > 0:
                glBindVertexArray(vao)
                glDrawArrays(GL_TRIANGLES, 0, count)
                self.draw_calls    += 1
                self.num_triangles += count // 3

    def _draw_bad_batch(self, shader: Shader) -> None:
        vao, count = self._bad_batch
        if not vao or count == 0:
            return

        shader.set_int("use_vertex_color", 1)
        shader.set_mat4("transform", _IDENTITY)
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, count)
        self.draw_calls    += 1
        self.num_triangles += count // 3

    # ---- OBJETOS NÃO BATCHÁVEIS ----

    def _render_unbatchable(self, objects: list, planes: list, shader: Shader) -> None:
        shader.set_int("use_vertex_color", 0)
        for obj in objects:
            if obj.may_be_batched:
                continue
            if not self._is_visible(obj, planes):
                continue

            lod         = self.current_lods[id(obj)]
            vao         = obj.get_vao(lod)
            index_count = obj.get_index_count(lod)
            if not vao:
                continue

            shader.set_mat4("transform",   obj.get_transform())
            shader.set_vec4("colorobject", obj.color)
            glBindVertexArray(vao)
            glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
            self.draw_calls    += 1
            self.num_triangles += index_count // 3

    # ---- RENDER PRINCIPAL ----

    def render_scene(self, objects: list[Object], camera: Camera, shader: Shader):
        aspect = camera.width / camera.height
        planes = camera.extract_frustum_planes(aspect)

        self.draw_calls    = 0
        self.num_triangles = 0
        self._compute_lods(objects, camera)

        shader.set_mat4("view", camera.view_matrix())
        shader.set_mat4("proj", camera.projection_matrix(aspect))

        if self.is_bad_batching_enabled:
            self._draw_bad_batch(shader)

        elif self.is_batching_enabled:
            self._draw_static_batches(objects, shader)
            self._render_unbatchable(objects, planes, shader)

        else:
            shader.set_int("use_vertex_color", 0)
            for obj in objects:
                if not self._is_visible(obj, planes):
                    continue

                lod         = self.current_lods[id(obj)]
                vao         = obj.get_vao(lod)
                index_count = obj.get_index_count(lod)
                if not vao:
                    continue

                shader.set_mat4("transform",   obj.get_transform())
                shader.set_vec4("colorobject", obj.color)
                glBindVertexArray(vao)
                glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, None)
                self.draw_calls    += 1
                self.num_triangles += index_count // 3

        return self.draw_calls, self.num_triangles