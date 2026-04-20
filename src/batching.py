# batching.py
import ctypes
from collections import defaultdict

import numpy as np
from OpenGL.GL import *

from lod import LOD


# ---- VAO BUILDER ----

def _build_vao(merged: np.ndarray) -> tuple:
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, merged.nbytes, merged, GL_STATIC_DRAW)

    stride = 10 * 4  # pos(3) + normal(3) + color(4) = 10 floats
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))
    glEnableVertexAttribArray(2)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return int(vao), len(merged)


# ---- VERTEX EXPANSION ----

def _object_to_vertices(obj, lod) -> np.ndarray | None:
    '''
    Transforma a malha em espaço local de um objeto em vértices em espaço de mundo,
    adequados para serem mesclados em um buffer de batch estático.

    Retorna um array float32 (N, 10): [pos_mundo(3), normal_mundo(3), cor(4)].
    As normais são transformadas pela inversa transposta da matriz do modelo (apenas R,
    sem translação/escala) para permanecerem corretas após escalas não uniformes.
    '''
    mesh = obj.get_mesh_data(lod)
    if mesh is None:
        return None

    model_m    = obj.get_transform()
    local_pos  = mesh.expanded_positions
    local_norm = mesh.normals
    n          = local_pos.shape[0]

    ones      = np.ones((n, 1), dtype=np.float32)
    world_pos = (np.hstack([local_pos, ones]) @ model_m.T)[:, :3]

    R3         = model_m[:3, :3]
    world_norm = local_norm @ R3.T
    nlen       = np.linalg.norm(world_norm, axis=1, keepdims=True)
    nlen       = np.where(nlen == 0, 1.0, nlen)
    world_norm /= nlen

    color_tile = np.broadcast_to(obj.color, (n, 4))
    return np.hstack([world_pos, world_norm, color_tile]).astype(np.float32)


# ---- STATIC BATCH BUILDER ----

def build_static_batches(objects) -> dict:
    '''
    Chamado UMA VEZ na inicialização. Agrupa objetos que podem ser batched por (ObjectType, LOD)
    e mescla suas geometrias em espaço de mundo em um único VAO por grupo.

    Em tempo de execução, o renderizador seleciona quais grupos desenhar com base nos LODs ativos,
    resultando em aproximadamente 1 draw call por tipo de objeto presente na cena.
    Retorna: {(ObjectType, LOD): (vao, quantidade_de_vertices)}
    '''
    groups: dict[tuple, list[np.ndarray]] = defaultdict(list)

    for obj in objects:
        if not obj.may_be_batched:
            continue
        for lod in LOD:
            verts = _object_to_vertices(obj, lod)
            if verts is not None:
                groups[(obj.object_type, lod)].append(verts)

    return {
        key: _build_vao(np.concatenate(chunks, axis=0))
        for key, chunks in groups.items()
    }


# ---- BAD BATCH BUILDER ----

def build_bad_batch(objects) -> tuple:
    '''
    Anti-pattern intencional: mescla TODOS os objetos batcháveis em um único VAO usando
    apenas LOD.HIGH, independentemente do tipo. Isso significa:
      - Não há troca de LOD por tipo em tempo de execução.
      - O frustum culling não pode descartar objetos individualmente.
      - Toda a geometria da cena é enviada para a GPU a cada frame.
    '''
    all_vertices = []

    for obj in objects:
        verts = _object_to_vertices(obj, LOD.HIGH)
        if verts is not None:
            all_vertices.append(verts)

    if not all_vertices:
        return None, 0

    return _build_vao(np.concatenate(all_vertices, axis=0))
