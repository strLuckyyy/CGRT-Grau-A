# lod.py
import enum
import numpy as np


class LOD(enum.Enum):
    LOW    = 0
    MEDIUM = 1
    HIGH   = 2


class LODDistance(enum.Enum):
    HIGH   = 60.0
    MEDIUM = 100.0
    LOW    = 250.0


def select_lod(camera, obj) -> LOD:
    distance = np.linalg.norm(camera.position - obj.position)

    if distance < LODDistance.HIGH.value:
        return LOD.HIGH
    elif distance < LODDistance.MEDIUM.value:
        return LOD.MEDIUM
    else:
        return LOD.LOW


def select_bad_lod(camera, obj) -> LOD:
    '''
    Limiares de LOD intencionalmente ruins: as transições acontecem em 15 e 25 unidades,
    causando pop-in agressivo e quase nenhum ganho de performance em média distância.
    '''
    distance = np.linalg.norm(camera.position - obj.position)

    if distance < 15:
        return LOD.HIGH
    elif distance < 25:
        return LOD.MEDIUM
    else:
        return LOD.LOW
