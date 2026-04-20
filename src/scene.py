# scene.py
import random
import numpy as np
from object import Object
from transform import make_transform
from fabric import (saloon, house_1, house_2, hotel, sheriff, shop,
					cactus, cart, lantern, water_drinker, ground, ground_way)


def _rgb(r, g, b) -> tuple:
	return (r / 255.0, g / 255.0, b / 255.0, 1.0)

def create_scene() -> list[Object]:
	objects: list[Object] = []

	# ---- BUILDINGS ----

	house_color = _rgb(65, 32, 20)
	X = 19.0

	left_types  = [house_1, sheriff, house_2, house_1, shop]
	right_types = [house_1, shop,    house_2, hotel,   house_2]


	for i, factory in enumerate(left_types):
		objects.append(factory(
			transform=make_transform(-X, 0.0, (i - 2) * 25.0, 1, 1, 1, Ry=90.0),
			color=house_color))

	for i, factory in enumerate(right_types):
		objects.append(factory(
			transform=make_transform(X, 0.0, (i - 2) * 25.0, 1, 1, 1, Ry=-90.0),
			color=house_color))

	objects.append(saloon(
		transform=make_transform(0.0, 0.0, -100.0, 3, 3, 3, Ry=-45.0),
		color=_rgb(206, 157, 86)))

	# ---- CACTI ----

	for _ in range(35):
		side  = random.choice([-1, 1])
		x_pos = side * random.uniform(20.0, 70.0)
		z_pos = random.uniform(-80.0, 80.0)
		s     = random.uniform(0.2, 0.5)
		objects.append(cactus(
			transform=make_transform(x_pos, 0.0, z_pos, s, s, s, Ry=random.uniform(0, 360)),
			color=(0.1, 0.6, 0.2, 1.0)))

	# ---- LANTERNS ----

	for pos in [(-5.0, 0.0, -25.0), (9.0, 0.0, -23.0),
				(-8.0, 0.0,  28.0), (9.0, 0.0,  45.0)]:
		ry = 90.0 if pos[0] < 0 else -90.0
		objects.append(lantern(
			transform=make_transform(pos[0], pos[1], pos[2], 1.5, 1.5, 1.5, Ry=ry),
			color=_rgb(92, 66, 45)))

	# ---- WATER DRINKER ----

	objects.append(water_drinker(
		transform=make_transform(12.0, 0.0, 0.0, 1.5, 1.5, 1.5, Ry=180.0),
		color=(0.8, 0.7, 0.6, 1.0)))

	# ---- CARTS ----

	for pos in [(-5.0, 0.5, -40.0), (3.0, 0.5, -5.0), (-3.0, 0.5, 45.0)]:
		objects.append(cart(
			transform=make_transform(pos[0], pos[1], pos[2], .6, .6, .6, Ry=90.0),
			color=_rgb(216, 182, 155)))

	# ---- GROUND ----

	objects.append(ground(
		transform=make_transform(0.0, -1.8, 0.0, 10.0, 1.0, 10.0),
		color=_rgb(204, 180, 150)))

	objects.append(ground_way(
		transform=make_transform(0.0, -1.6, 0.0, 0.2, 1.0, 1.5),
		color=_rgb(205, 147, 81)))

	return objects
