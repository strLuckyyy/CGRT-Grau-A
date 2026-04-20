# fabric.py
import numpy as np
import bounding as bd
from lod import LOD
from object import Object, ObjectType
from transform import make_transform


# ---- LOD FILE MAPS ----

_SALOON_LOD = {
    LOD.HIGH.value:   r"Saloon\Saloon_LOD0.obj",
    LOD.MEDIUM.value: r"Saloon\Saloon_LOD1.obj",
    LOD.LOW.value:    r"Saloon\Saloon_LOD2.obj",
}
_HOUSE_1_LOD = {
    LOD.HIGH.value:   r"House1\House_LOD0.obj",
    LOD.MEDIUM.value: r"House1\House_LOD1.obj",
    LOD.LOW.value:    r"House1\House_LOD2.obj",
}
_HOUSE_2_LOD = {
    LOD.HIGH.value:   r"House2\House_LOD0.obj",
    LOD.MEDIUM.value: r"House2\House_LOD1.obj",
    LOD.LOW.value:    r"House2\House_LOD2.obj",
}
_HOTEL_LOD = {
    LOD.HIGH.value:   r"Hotel\Hotel_LOD0.obj",
    LOD.MEDIUM.value: r"Hotel\Hotel_LOD1.obj",
    LOD.LOW.value:    r"Hotel\Hotel_LOD2.obj",
}
_SHERIFF_LOD = {
    LOD.HIGH.value:   r"Sheriff\Sheriff_LOD0.obj",
    LOD.MEDIUM.value: r"Sheriff\Sheriff_LOD1.obj",
    LOD.LOW.value:    r"Sheriff\Sheriff_LOD2.obj",
}
_SHOP_LOD = {
    LOD.HIGH.value:   r"Shop\Shop_LOD0.obj",
    LOD.MEDIUM.value: r"Shop\Shop_LOD1.obj",
    LOD.LOW.value:    r"Shop\Shop_LOD2.obj",
}
_CART_LOD = {
    LOD.HIGH.value:   r"Cart\Cart_LOD0.obj",
    LOD.MEDIUM.value: r"Cart\Cart_LOD1.obj",
    LOD.LOW.value:    r"Cart\Cart_LOD2.obj",
}
_CACTUS_LOD = {
    LOD.HIGH.value:   r"Cactus\Cactus_LOD0.obj",
    LOD.MEDIUM.value: r"Cactus\Cactus_LOD1.obj",
    LOD.LOW.value:    r"Cactus\Cactus_LOD2.obj",
}
_LANTERN_LOD = {
    LOD.HIGH.value:   r"prop\Lantern_LOD0.obj",
    LOD.MEDIUM.value: r"prop\Lantern_LOD1.obj",
    LOD.LOW.value:    r"prop\Lantern_LOD2.obj",
}
_WATER_DRINKER_LOD = {
    LOD.HIGH.value:   r"prop\WDrinker_LOD0.obj",
    LOD.MEDIUM.value: r"prop\WDrinker_LOD1.obj",
    LOD.LOW.value:    r"prop\WDrinker_LOD2.obj",
}
_GROUND_LOD = {
    LOD.HIGH.value:   r"Ground\Ground.obj",
    LOD.MEDIUM.value: r"Ground\Ground.obj",
    LOD.LOW.value:    r"Ground\Ground.obj",
}
_GROUND_WAY_LOD = {
    LOD.HIGH.value:   r"Ground\Ground_Way.obj",
    LOD.MEDIUM.value: r"Ground\Ground_Way.obj",
    LOD.LOW.value:    r"Ground\Ground_Way.obj",
}


# ---- INTERNAL FACTORY HELPER ----

def _make(lod_files, color, bound_type, may_be_batched, object_type, transform) -> Object:
    return Object(
        lod_files=lod_files,
        color=color,
        bound_type=bound_type,
        may_be_batched=may_be_batched,
        object_type=object_type,
        transform=transform,
    )


# ---- PUBLIC FACTORIES ----

def saloon(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_SALOON_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def house_1(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_HOUSE_1_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def house_2(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_HOUSE_2_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def hotel(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_HOTEL_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def sheriff(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_SHERIFF_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def shop(transform=make_transform(), color=(0.5, 0.5, 0.5, 1.0)) -> Object:
    return _make(_SHOP_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.BUILDING, transform)

def cactus(transform=make_transform(), color=(0.2, 0.7, 0.2, 1.0)) -> Object:
    return _make(_CACTUS_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.CACTUS, transform)

def cart(transform=make_transform(), color=(0.8, 0.2, 0.2, 1.0)) -> Object:
    return _make(_CART_LOD, color, bd.BoundingType.AABB, False,
                 ObjectType.CART, transform)

def lantern(transform=make_transform(), color=(0.8, 0.8, 0.2, 1.0)) -> Object:
    return _make(_LANTERN_LOD, color, bd.BoundingType.AABB, False,
                 ObjectType.LANTERN, transform)

def water_drinker(transform=make_transform(), color=(0.2, 0.8, 0.8, 1.0)) -> Object:
    return _make(_WATER_DRINKER_LOD, color, bd.BoundingType.AABB, False,
                 ObjectType.PROP, transform)

def ground(transform=make_transform(), color=(0.5, 1.0, 0.5, 1.0)) -> Object:
    return _make(_GROUND_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.GROUND, transform)

def ground_way(transform=make_transform(), color=(0.7, 0.7, 0.7, 1.0)) -> Object:
    return _make(_GROUND_WAY_LOD, color, bd.BoundingType.AABB, True,
                 ObjectType.GROUND, transform)