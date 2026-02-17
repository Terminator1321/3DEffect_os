import glfw
from OpenGL.GL import *
from PIL import Image
from Utility import getHeadCoor
import math
from collections import deque
import mss
import numpy as np
import threading
import time

width, height = 800, 500
texture = None
last_x = 0
last_y = 0
canRun = True
class Smoother:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.x_buffer = deque(maxlen=window_size)
        self.y_buffer = deque(maxlen=window_size)
        
    def smooth(self, x, y):
        self.x_buffer.append(x)
        self.y_buffer.append(y)
        
        avg_x = sum(self.x_buffer) / len(self.x_buffer)
        avg_y = sum(self.y_buffer) / len(self.y_buffer)
        
        return avg_x, avg_y

smoother = Smoother(window_size=8)
last_x, last_y = 0.0, 0.0

screen_capture = None
capture_lock = threading.Lock()
capture_running = True

def capture_screen_thread():
    global screen_capture,canRun
    
    with mss.mss() as sct:
        if len(sct.monitors) > 2:
            monitor = sct.monitors[2]
            canRun = True
        else:
            print("no second monitor detected")
            canRun = False
            return
        
        while capture_running:
            img = sct.grab(monitor)
            frame = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
            with capture_lock:
                screen_capture = frame
            time.sleep(1/60)

def create_texture_from_image(img):
    img_data = img.convert("RGBA").tobytes()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0,GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex_id

def update_texture(tex_id, img):
    img_rgba = img.convert("RGBA")
    img_data = img_rgba.tobytes()
    
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, img_rgba.width, img_rgba.height,GL_RGBA, GL_UNSIGNED_BYTE, img_data)

def draw_room(x, y,sensitivity=1.2,layers=8,depth_strength=0.35,texture=None,input_range=0.2,parallax_scale=1.5):
    x_norm = x / input_range
    y_norm = y / input_range
    
    x_norm = max(-1.0, min(1.0, x_norm))
    y_norm = max(-1.0, min(1.0, y_norm))
    
    x_offset = x_norm * sensitivity * parallax_scale
    y_offset = y_norm * sensitivity * parallax_scale

    rects = []
    for i in range(layers):
        t = 0 if layers == 1 else i / (layers - 1)
        t_curved = math.pow(t, 1.2)
        scale = 1.0 - t_curved * depth_strength
        scale = max(scale, 0.05)

        w = width * scale
        h = height * scale

        max_offset_x = (width - w) / 2 * parallax_scale
        max_offset_y = (height - h) / 2 * parallax_scale

        offset_x = -x_offset * max_offset_x
        offset_y = -y_offset * max_offset_y

        cx = width / 2 + offset_x
        cy = height / 2 + offset_y

        left = cx - w / 2
        right = cx + w / 2
        top = cy - h / 2
        bottom = cy + h / 2

        rects.append((left, top, right, bottom))

    for idx, (l, t, r, b) in enumerate(rects):
        alpha = 1.0 - (idx / len(rects)) * 0.7
        glColor4f(1, 1, 1, alpha)
        glBegin(GL_LINES)
        glVertex2f(l, t); glVertex2f(r, t)
        glVertex2f(r, t); glVertex2f(r, b)
        glVertex2f(r, b); glVertex2f(l, b)
        glVertex2f(l, b); glVertex2f(l, t)
        glEnd()

    if texture is None or len(rects) < 2:
        return

    glBindTexture(GL_TEXTURE_2D, texture)
    l1, t1, r1, b1 = rects[0]
    l2, t2, r2, b2 = rects[-1]

    glBegin(GL_QUADS)
    glColor4f(0.75, 0.75, 0.75, 0.85)
    glTexCoord2f(1, 0); glVertex2f(l1, t1)
    glTexCoord2f(0, 0); glVertex2f(l2, t2)
    glTexCoord2f(0, 1); glVertex2f(l2, b2)
    glTexCoord2f(1, 1); glVertex2f(l1, b1)

    glColor4f(0.4, 0.4, 0.4, 0.3)
    glTexCoord2f(0, 0); glVertex2f(l1, t1)
    glTexCoord2f(1, 0); glVertex2f(l2, t2)
    glTexCoord2f(1, 1); glVertex2f(l2, b2)
    glTexCoord2f(0, 1); glVertex2f(l1, b1)

    glColor4f(0.75, 0.75, 0.75, 0.85)
    glTexCoord2f(1, 0); glVertex2f(r2, t2)
    glTexCoord2f(0, 0); glVertex2f(r1, t1)
    glTexCoord2f(0, 1); glVertex2f(r1, b1)
    glTexCoord2f(1, 1); glVertex2f(r2, b2)

    glColor4f(0.4, 0.4, 0.4, 0.3)
    glTexCoord2f(0, 0); glVertex2f(r2, t2)
    glTexCoord2f(1, 0); glVertex2f(r1, t1)
    glTexCoord2f(1, 1); glVertex2f(r1, b1)
    glTexCoord2f(0, 1); glVertex2f(r2, b2)

    glColor4f(0.55, 0.55, 0.55, 0.65)
    glTexCoord2f(0, 1); glVertex2f(l1, t1)
    glTexCoord2f(1, 1); glVertex2f(r1, t1)
    glTexCoord2f(1, 0); glVertex2f(r2, t2)
    glTexCoord2f(0, 0); glVertex2f(l2, t2)

    glColor4f(0.55, 0.55, 0.55, 0.65)
    glTexCoord2f(0, 1); glVertex2f(l2, b2)
    glTexCoord2f(1, 1); glVertex2f(r2, b2)
    glTexCoord2f(1, 0); glVertex2f(r1, b1)
    glTexCoord2f(0, 0); glVertex2f(l1, b1)
    glEnd()

    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(l2, t2)
    glTexCoord2f(1, 0); glVertex2f(r2, t2)
    glTexCoord2f(1, 1); glVertex2f(r2, b2)
    glTexCoord2f(0, 1); glVertex2f(l2, b2)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)

    glBegin(GL_QUADS)
    glColor4f(0, 0, 0, 0.15)
    glVertex2f(0, 0)
    glColor4f(0, 0, 0, 0)
    glVertex2f(width * 0.2, 0)
    glVertex2f(width * 0.2, height)
    glColor4f(0, 0, 0, 0.15)
    glVertex2f(0, height)

    glColor4f(0, 0, 0, 0)
    glVertex2f(width * 0.8, 0)
    glColor4f(0, 0, 0, 0.15)
    glVertex2f(width, 0)
    glVertex2f(width, height)
    glColor4f(0, 0, 0, 0)
    glVertex2f(width * 0.8, height)
    glEnd()

    glColor4f(1, 1, 1, 1)

def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

def main():
    global width, height, texture, last_x, last_y, capture_running

    if not glfw.init():
        return

    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    width = mode.size.width
    height = mode.size.height

    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.FALSE)
    glfw.window_hint(glfw.AUTO_ICONIFY, glfw.FALSE)
    
    window = glfw.create_window(width, height, "Parallax Room", monitor, None)
    
    if not window:
        glfw.terminate()
        return
        
    glfw.make_context_current(window)

    glfw.set_window_attrib(window, glfw.FLOATING, glfw.TRUE)
    glfw.set_window_attrib(window, glfw.AUTO_ICONIFY, glfw.FALSE)
    
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)

    capture_thread = threading.Thread(target=capture_screen_thread, daemon=True)
    capture_thread.start()
    
    while screen_capture is None:
        if not canRun:
            print("Capture not available. Closing window safely.")
            glfw.set_window_should_close(window, True)
            break
        time.sleep(0.01)
    
    with capture_lock:
        texture = create_texture_from_image(screen_capture)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)

    smoothing_factor = 0.15
    
    frame_count = 0
    
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        x, y = getHeadCoor()
        
        smoothed_x, smoothed_y = smoother.smooth(x, y)
        
        last_x = last_x + (smoothed_x - last_x) * smoothing_factor
        last_y = last_y + (smoothed_y - last_y) * smoothing_factor

        if screen_capture is not None:
            with capture_lock:
                update_texture(texture, screen_capture)

        draw_room( -last_x, -last_y, sensitivity=1.2, layers=8, depth_strength=0.35, texture=texture, input_range=0.3, parallax_scale=1.1)

        glfw.swap_buffers(window)
        glfw.poll_events()
        
        frame_count += 1

    capture_running = False
    capture_thread.join(timeout=1.0)
    
    glfw.terminate()

if __name__ == "__main__":
    main()