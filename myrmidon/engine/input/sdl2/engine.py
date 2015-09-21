"""
Myrmidon
Copyright (c) 2010 Fiona Burrows
 
Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:
 
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
 
---------------------

- BACKEND FILE -
- INPUT        -

A Pygame (and conversely, SDL) driven backend for user input.

"""

#import pygame
#from pygame.locals import *
import sdl2
import sdl2.ext
import ctypes


from myrmidon import Entity
from myrmidon.consts import *


class Myrmidon_Backend(object):

    keys_pressed = []
    last_keys_pressed = []
    event_store = []
    mouse = None
    flush_events = True
    disable_input = False
        
    def __init__(self):
        #pygame.key.set_repeat(10, 0)
        self.keys_pressed = sdl2.keyboard.SDL_GetKeyboardState(None)
        self.last_keys_pressed = self.keys_pressed


    def process_input(self):
        if not self.mouse:
            self.mouse = self.Mouse()
            self.mouse.z = -512
            self.mouse.visible = True
            self.mouse.collision_on = True
            self.mouse.collision_type = COLLISION_TYPE_POINT
            self.initialise_mouse_state()

        if self.disable_input:
            self.initialise_mouse_state()
            return
                
        self.mouse.wheel_down = False
        self.mouse.wheel_up = False
        self.mouse.left_down = False
        self.mouse.left_up = False
        self.mouse.middle_down = False
        self.mouse.middle_up = False
        self.mouse.right_down = False
        self.mouse.right_up = False

        self.last_keys_pressed = self.keys_pressed
        sdl2.SDL_PumpEvents()
        self.keys_pressed = sdl2.keyboard.SDL_GetKeyboardState(None)

        for i in range(0, 200):
            if self.keys_pressed[i] == 1:
                print("yay")




        #print(self.keys_pressed[sdl2.SDLK_ESCAPE])


        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        relx = ctypes.c_int(0)
        rely = ctypes.c_int(0)
        self.mouse.pos = sdl2.mouse.SDL_GetMouseState(x, y)

        sdl2.mouse.SDL_GetRelativeMouseState(relx, rely)
        self.mouse.rel = (relx.value, rely.value)
        self.mouse.x = x.value
        self.mouse.y = y.value

        self.event_store = []
        #sdl2.SDL_PollEvent()

        for event in sdl2.ext.get_events():

            self.event_store.append(event)
            if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                print("mouse button")
                if event.button == 4:
                    self.mouse.wheel_up = True
                elif event.button == 5:
                    self.mouse.wheel_down = True
                elif event.button == 1:
                    self.mouse.left = True
                    self.mouse.left_down = True
                elif event.button == 2:
                    self.mouse.middle = True
                    self.mouse.middle_down = True
                elif event.button == 3:
                    self.mouse.right = True
                    self.mouse.right_down = True
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse.left = False
                    self.mouse.left_up = True
                if event.button == 2:
                    self.mouse.middle = False
                    self.mouse.middle_up = True
                if event.button == 3:
                    self.mouse.right = False
                    self.mouse.right_up = True

        if self.flush_events:
            sdl2.SDL_FlushEvents(sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)

    def keyboard_key_down(self, key_code):
        if self.keys_pressed[key_code]:
            return True
        return False
        
    def keyboard_key_released(self, key_code):
         if self.last_keys_pressed[key_code] and not self.keys_pressed[key_code]:
              return True
         return False

    def initialise_mouse_state(self):
        self.mouse.pos = (0, 0)
        self.mouse.rel = (0, 0)
        self.mouse.left = False
        self.mouse.middle = False
        self.mouse.right = False
        self.mouse.left_down = False
        self.mouse.left_up = False
        self.mouse.middle_down = False
        self.mouse.middle_up = False
        self.mouse.right_down = False
        self.mouse.right_up = False
        self.mouse.wheel_up = False
        self.mouse.wheel_down = False
                
    class Mouse(Entity):
        """ Record for holding mouse info """

        _visible = True
        @property
        def visible(self):
            return self._visible

        @visible.setter
        def visible(self, value):
            self._visible = value
            sdl2.mouse.SDL_ShowCursor(value)

        @visible.deleter
        def visible(self):
            self._visible = False

        def set_pos(self, new_pos):
            """
            Pass in a tuple corrisponding to the screen position we want
            the mouse to sit at.
            """
            self.pos = new_pos
            self.x, self.y = self.pos
            sdl2.mouse.SDL_WarpMouseInWindow(new_pos)
