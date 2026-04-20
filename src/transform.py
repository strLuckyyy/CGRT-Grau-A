# transform.py
import numpy as np


def make_transform(
    Tx: float = 0.0, Ty: float = 0.0, Tz: float = 0.0,
    Sx: float = 1.0, Sy: float = 1.0, Sz: float = 1.0,
    Rx: float = 0.0, Ry: float = 0.0, Rz: float = 0.0,
) -> np.ndarray:
    '''
    Constrói e retorna uma matriz de modelo 4x4 no formato T * Rz * Ry * Rx * S.

    Todos os ângulos de rotação estão em graus.
    Retorna um ndarray float32 pronto para envio ao OpenGL.
    '''
    rx, ry, rz = np.radians([Rx, Ry, Rz])

    T = np.array([
        [1, 0, 0, Tx],
        [0, 1, 0, Ty],
        [0, 0, 1, Tz],
        [0, 0, 0,  1],
    ], dtype=np.float32)

    S = np.array([
        [Sx,  0,  0, 0],
        [ 0, Sy,  0, 0],
        [ 0,  0, Sz, 0],
        [ 0,  0,  0, 1],
    ], dtype=np.float32)

    cx, sx = np.cos(rx), np.sin(rx)
    rotX = np.array([
        [1,   0,  0, 0],
        [0,  cx, -sx, 0],
        [0,  sx,  cx, 0],
        [0,   0,  0, 1],
    ], dtype=np.float32)

    cy, sy = np.cos(ry), np.sin(ry)
    rotY = np.array([
        [ cy, 0, sy, 0],
        [  0, 1,  0, 0],
        [-sy, 0, cy, 0],
        [  0, 0,  0, 1],
    ], dtype=np.float32)

    cz, sz = np.cos(rz), np.sin(rz)
    rotZ = np.array([
        [cz, -sz, 0, 0],
        [sz,  cz, 0, 0],
        [ 0,   0, 1, 0],
        [ 0,   0, 0, 1],
    ], dtype=np.float32)

    return T @ rotZ @ rotY @ rotX @ S


def uniform_scale_transform(
    Tx: float = 0.0, Ty: float = 0.0, Tz: float = 0.0,
    S:  float = 1.0,
    Rx: float = 0.0, Ry: float = 0.0, Rz: float = 0.0,
) -> np.ndarray:
    '''Wrapper de conveniência para objetos que usam um único valor de escala uniforme.'''
    return make_transform(Tx, Ty, Tz, S, S, S, Rx, Ry, Rz)