# loader.py
import ctypes
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
from OpenGL.GL import *

ASSETS_DIR = "./assets/"


@dataclass
class MeshData:
    '''
    Estado da malha no lado da GPU junto com arrays no lado da CPU necessários para batching estático.

    positions e normals são mantidos na RAM porque build_static_batches()
    precisa transformá-los para o espaço de mundo na inicialização. Após o batching,
    eles não são mais acessados.
    '''
    vao:                int
    vbo:                int
    ebo:                int
    vertex_count:       int
    index_count:        int
    positions:          NDArray[np.float32] = field(repr=False)  # vértices únicos (para bounding)
    normals:            NDArray[np.float32] = field(repr=False)  # expandido por índice (para batching)
    expanded_positions: NDArray[np.float32] = field(repr=False)  # expandido por índice (para batching)


def load_obj(filepath: str) -> MeshData | None:
    '''
    Faz o parse de um arquivo Wavefront OBJ e envia sua geometria para a GPU.

    Faces são trianguladas (método fan) e vértices são deduplicados pelo par
    (índice_posição, índice_normal). Essa deduplicação reduz o tamanho do
    vertex buffer e é necessária para indexação correta com EBO.
    '''
    raw_vertices:       list[list[float]] = []
    raw_normals:        list[list[float]] = []
    vbuffer:            list[float]       = []
    positions_list:     list[list[float]] = []
    normals_list:       list[list[float]] = []
    expanded_pos_list:  list[list[float]] = []
    expanded_norm_list: list[list[float]] = []

    vertex_map: dict[tuple, int] = {}
    indices:    list[int]        = []

    try:
        with open(ASSETS_DIR + filepath, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue

                if parts[0] == "v":
                    raw_vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])

                elif parts[0] == "vn":
                    raw_normals.append([float(parts[1]), float(parts[2]), float(parts[3])])

                elif parts[0] == "f":
                    face_indices      = []
                    face_norm_indices = []

                    for token in parts[1:]:
                        subparts = token.split("/")
                        face_indices.append(int(subparts[0]) - 1)
                        if len(subparts) > 2 and subparts[2]:
                            face_norm_indices.append(int(subparts[2]) - 1)
                        else:
                            face_norm_indices.append(-1)

                    # Triangulação em fan: o vértice 0 é compartilhado entre todos os triângulos
                    for i in range(1, len(face_indices) - 1):
                        for idx in [0, i, i + 1]:
                            v_idx  = face_indices[idx]
                            vn_idx = face_norm_indices[idx]
                            key    = (v_idx, vn_idx)

                            if key not in vertex_map:
                                vertex_map[key] = len(positions_list)
                                pos  = raw_vertices[v_idx]
                                norm = raw_normals[vn_idx] if vn_idx != -1 else [0.0, 1.0, 0.0]
                                vbuffer.extend(pos)
                                vbuffer.extend(norm)
                                positions_list.append(pos)
                                normals_list.append(norm)

                            indices.append(vertex_map[key])

                            # Arrays expandidos têm uma entrada por índice — necessário para batching
                            pos  = raw_vertices[v_idx]
                            norm = raw_normals[vn_idx] if vn_idx != -1 else [0.0, 1.0, 0.0]
                            expanded_pos_list.append(pos)
                            expanded_norm_list.append(norm)

    except Exception as e:
        print(f"[Loader] Error loading '{filepath}': {e}")
        return None

    if not vbuffer:
        print(f"[Loader] No vertices found in '{filepath}'")
        return None

    varray       = np.array(vbuffer,            dtype=np.float32)
    pos_arr      = np.array(positions_list,     dtype=np.float32)
    idx_arr      = np.array(indices,            dtype=np.uint32)
    exp_pos_arr  = np.array(expanded_pos_list,  dtype=np.float32)
    exp_norm_arr = np.array(expanded_norm_list, dtype=np.float32)
    stride = 6 * 4  # pos(3) + normal(3) floats

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, varray.nbytes, varray, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx_arr.nbytes, idx_arr, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    unique_verts = len(varray) // 6
    print(f"[Loader] {filepath}: {unique_verts} unique verts, {len(indices)} indices "
          f"(saved {len(indices) - unique_verts} duplicates via EBO)")

    return MeshData(
        vao=int(vao),
        vbo=int(vbo),
        ebo=int(ebo),
        vertex_count=unique_verts,
        index_count=len(indices),
        positions=pos_arr,
        normals=exp_norm_arr,
        expanded_positions=exp_pos_arr,
    )
