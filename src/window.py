# window.py
import glfw
import numpy as np
from OpenGL.GL import *

from camera import Camera
from object import Object
from shader import Shader
from render import Renderer
from debug  import DebugRenderer


class Window:
    '''
    Wrapper da janela GLFW e responsável pelo loop principal.

    Possui Camera, Shader, Renderer e DebugRenderer. Centraliza todos os
    callbacks do GLFW e traduz inputs do teclado em mudanças de flags do renderer,
    além de controlar o ciclo de renderização, debug e swap de buffers por frame.
    '''

    def __init__(self, width: int = 1280, height: int = 720, title: str = "Wild West") -> None:
        self.width  = width
        self.height = height
        self.title  = title

        self.dt               = 0.0
        self.fps              = 0
        self._fps_counter     = 0
        self._fps_accumulator = 0.0

        self._glfw_window = None
        self._build()

        self.camera = Camera(width=self.width, height=self.height)
        self.shader = Shader()
        self.render = Renderer()
        self.debug  = DebugRenderer()

    # ---- SETUP ----

    def _build(self) -> None:
        glfw.init()

        window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not window:
            glfw.terminate()
            exit()

        self._glfw_window = window
        glfw.make_context_current(self._glfw_window)
        glfw.set_input_mode(self._glfw_window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        glfw.set_window_size_callback(self._glfw_window, self._on_resize)
        glfw.set_cursor_pos_callback(self._glfw_window,  self._on_mouse)
        glfw.set_key_callback(self._glfw_window,         self._on_key)

        print("GPU:", glGetString(GL_RENDERER))
        print("OpenGL:", glGetString(GL_VERSION))

    # ---- CALLBACKS ----

    def _on_resize(self, window, width: int, height: int) -> None:
        self.width  = width
        self.height = height
        self.camera.update_window_size(width, height)

    def _on_mouse(self, window, xpos: float, ypos: float) -> None:
        cam = self.camera
        if cam.first_mouse:
            cam.last_x, cam.last_y = xpos, ypos
            cam.first_mouse = False

        dx = (xpos - cam.last_x) * 0.1
        dy = (cam.last_y - ypos) * 0.1
        cam.last_x, cam.last_y = xpos, ypos

        cam.yaw   += dx
        cam.pitch  = max(-89.0, min(89.0, cam.pitch + dy))

    def _on_key(self, window, key, scancode, action, mods) -> None:
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(self._glfw_window, True)
        self._toggle_optimizations(key)
        self._toggle_debug(key)

    # ---- TOGGLES DE OTIMIZAÇÃO ----

    def _toggle_optimizations(self, key) -> None:
        r = self.render

        if key == glfw.KEY_1:
            all_on = r.is_lod_enabled and r.is_frustum_culling_enabled and r.is_batching_enabled
            r.is_lod_enabled             = not all_on
            r.is_frustum_culling_enabled = not all_on
            r.is_batching_enabled        = not all_on

        if key == glfw.KEY_2: r.is_lod_enabled             = not r.is_lod_enabled
        if key == glfw.KEY_3: r.is_frustum_culling_enabled = not r.is_frustum_culling_enabled
        if key == glfw.KEY_4: r.is_batching_enabled        = not r.is_batching_enabled

        if key == glfw.KEY_5:
            all_on = r.is_bad_lod_enabled and r.is_bad_frustum_culling_enabled and r.is_bad_batching_enabled
            r.is_bad_lod_enabled             = not all_on
            r.is_bad_frustum_culling_enabled = not all_on
            r.is_bad_batching_enabled        = not all_on

        if key == glfw.KEY_6: r.is_bad_lod_enabled             = not r.is_bad_lod_enabled
        if key == glfw.KEY_7: r.is_bad_frustum_culling_enabled = not r.is_bad_frustum_culling_enabled
        if key == glfw.KEY_8: r.is_bad_batching_enabled        = not r.is_bad_batching_enabled

        # Garante que versões boas e ruins de uma mesma feature não estejam ativas ao mesmo tempo
        self._mutex()

    def _toggle_debug(self, key) -> None:
        d = self.debug
        if key == glfw.KEY_9:
            d.show_bounding = not d.show_bounding
            print(f"[9] Debug Bounding: {'ON' if d.show_bounding else 'OFF'}")
        if key == glfw.KEY_0:
            d.show_lod = not d.show_lod
            print(f"[0] Debug LOD Colors: {'ON' if d.show_lod else 'OFF'}")

    def _mutex(self) -> None:
        r = self.render
        if r.is_lod_enabled:                   r.is_bad_lod_enabled             = False
        elif r.is_bad_lod_enabled:             r.is_lod_enabled                 = False
        if r.is_frustum_culling_enabled:       r.is_bad_frustum_culling_enabled = False
        elif r.is_bad_frustum_culling_enabled: r.is_frustum_culling_enabled     = False
        if r.is_batching_enabled:              r.is_bad_batching_enabled        = False
        elif r.is_bad_batching_enabled:        r.is_batching_enabled            = False

    # ---- MOVIMENTO ----

    def _movement(self) -> None:
        cam   = self.camera
        win   = self._glfw_window
        shift = glfw.get_key(win, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
        speed = cam.speed * self.dt * (6.0 if shift else 1.0)

        front = np.array([
            np.cos(np.radians(cam.yaw)) * np.cos(np.radians(cam.pitch)),
            np.sin(np.radians(cam.pitch)),
            np.sin(np.radians(cam.yaw)) * np.cos(np.radians(cam.pitch)),
        ], dtype=np.float32)
        front /= np.linalg.norm(front)
        right  = np.cross(front, cam.up)
        right /= np.linalg.norm(right)

        if glfw.get_key(win, glfw.KEY_W) == glfw.PRESS: cam.position += front * speed
        if glfw.get_key(win, glfw.KEY_S) == glfw.PRESS: cam.position -= front * speed
        if glfw.get_key(win, glfw.KEY_A) == glfw.PRESS: cam.position -= right * speed
        if glfw.get_key(win, glfw.KEY_D) == glfw.PRESS: cam.position += right * speed

    # ---- MÉTRICAS ----

    def _update_fps(self) -> None:
        self._fps_counter     += 1
        self._fps_accumulator += self.dt
        if self._fps_accumulator >= 1.0:
            self.fps              = self._fps_counter
            self._fps_counter     = 0
            self._fps_accumulator -= 1.0

    def _lod_metric(self) -> str:
        if self.render.is_bad_lod_enabled: return "BAD"
        if self.render.is_lod_enabled:     return "ON"
        return "OFF"

    def _fc_metric(self) -> str:
        if self.render.is_bad_frustum_culling_enabled: return "BAD"
        if self.render.is_frustum_culling_enabled:     return "ON"
        return "OFF"

    def _bat_metric(self) -> str:
        if self.render.is_bad_batching_enabled: return "BAD"
        if self.render.is_batching_enabled:     return "ON"
        return "OFF"

    def _show_metrics(self) -> None:
        r = self.render
        glfw.set_window_title(self._glfw_window,
            f"{self.title} | "
            f"FPS: {self.fps} | "
            f"Draw Calls: {r.draw_calls} | "
            f"Tris: {r.num_triangles} | "
            f"LOD: {self._lod_metric()} | "
            f"FC: {self._fc_metric()} | "
            f"Bat: {self._bat_metric()}"
        )

    def _print_controls(self) -> None:
        print("\n--- Controles ---")
        print("  WASD + Shift / Mouse  : movimentação da câmera")
        print("  1  : ativa/desativa TODAS as otimizações corretas")
        print("  2  : LOD correto")
        print("  3  : Frustum Culling correto")
        print("  4  : Batching correto (por tipo)")
        print("  5  : ativa/desativa TODAS as versões ruins")
        print("  6  : LOD ruim")
        print("  7  : Frustum Culling ruim")
        print("  8  : Batching ruim (VAO único)")
        print("  9  : Debug Bounding (wireframe branco)")
        print("  0  : Debug LOD (verde=HIGH  amarelo=MEDIUM  vermelho=LOW)")
        print("  ESC: sair\n")

    # ---- LOOP PRINCIPAL ----

    def run(self, objects: list[Object]) -> None:
        glEnable(GL_DEPTH_TEST)
        prev_time = glfw.get_time()

        self._print_controls()
        self.render.init_batches(objects)

        while not glfw.window_should_close(self._glfw_window):
            now       = glfw.get_time()
            self.dt   = now - prev_time
            prev_time = now

            self._update_fps()

            glClearColor(0.08, 0.08, 0.10, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glViewport(0, 0, self.width, self.height)

            self.shader.use()
            self._movement()
            self.render.render_scene(objects, self.camera, self.shader)
            self.debug.render(objects, self.camera, self.render.current_lods)
            self._show_metrics()

            glfw.swap_buffers(self._glfw_window)
            glfw.poll_events()

        glfw.terminate()