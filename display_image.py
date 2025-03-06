from PIL import Image
import io

from time import perf_counter

import numpy as np
import pygame as pg

from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


class ImageRenderer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.vertex_shader_path = r'shaders/vertex_shader.glsl'
        self.fragment_shader_path = r'shaders/fragment_shader.glsl'
        
        self.vertices = np.array([
            # positions         # texture coords
            -1.0, -1.0, 0.0,    0.0, 0.0,
             1.0, -1.0, 0.0,    1.0, 0.0,
             1.0,  1.0, 0.0,    1.0, 1.0,
            -1.0,  1.0, 0.0,    0.0, 1.0,
        ], dtype=np.float32)
        
        self.indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        self.init_GL_context()
     
        self.shader = self.load_shaders()
        
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
        self.texture = glGenTextures(1)

        self.setup_buffers()
        self.load_texture()

    def init_GL_context(self):
        
        # PyGame init
        pg.init()
        display = (800, 600)
        pg.display.set_mode(display, DOUBLEBUF | OPENGL)

        # GLSL init
        glClearColor(0.1, 0.2, 0.2, 1.0)
        

    def load_shaders(self):
        
        with open(self.vertex_shader_path, 'r') as file:
            vertex_shader_code = file.read()
        
        with open(self.fragment_shader_path, 'r') as file:
            fragment_shader_code = file.read()

        vertex_shader = compileShader(vertex_shader_code, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
        
        shader = compileProgram(vertex_shader, fragment_shader)
        
        return shader
    
    def setup_buffers(self):
        
        glBindVertexArray(self.vao)
        
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * self.vertices.itemsize, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * self.vertices.itemsize, ctypes.c_void_p(3 * self.vertices.itemsize))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def load_texture(self):
        
        image = Image.open(self.image_path)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(list(image.getdata()), np.uint8)

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
    def render(self):
        
        glUseProgram(self.shader)

        glBindVertexArray(self.vao)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def display(self):
        
        running = True
        while running:
            for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
        
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            self.render()

            pg.display.flip()
            
        self.quit()

    def quit(self):
        
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        
        glDeleteTextures(1, (self.texture,))
        
        glDeleteProgram(self.shader)
        pg.quit()


if __name__ == '__main__':
    renderer = ImageRenderer(r'images/image.jpg')
    renderer.display()