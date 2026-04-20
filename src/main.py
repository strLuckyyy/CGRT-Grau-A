import os
import numpy as np
from window import Window
from scene import create_scene


if __name__ == "__main__":
	os.system("cls" if os.name == "nt" else "clear")

	win = Window(width=1280, height=720, title="Velho Oeste")
	
	win.run(create_scene())
