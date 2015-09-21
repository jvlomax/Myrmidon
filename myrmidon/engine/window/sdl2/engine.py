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
- WINDOW       -

A sdl2-based window creation and handling backend.

"""

import os, sdl2
import sdl2.ext

from myrmidon import Game, MyrmidonError, BaseFont


class Myrmidon_Backend(object):
    opengl = False
    screen = None
    flags = 0

    def __init__(self):
        if Game.engine_def['gfx'] in ["opengl", "modern_opengl"]:
            self.opengl = True
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        sdl2.ext.init()

        if self.opengl:
            #pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLEBUFFERS, 1)
            #pygame.display.gl_set_attribute(pygame.locals.GL_MULTISAMPLESAMPLES, 4)
            #sdl2.SDL_GL_SetAttribute(sdl2.SDL_Swap32, 0)
            #pygame.display.gl_set_attribute(pygame.locals.GL_DEPTH_SIZE, 16)
            self.flags = sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_GL_DOUBLEBUFFER

            pass
        if Game.full_screen:
            #self.flags |= sdl2.SDL_WINDOW_FULLSCREEN
            pass

        # Check we can set the resolution at this mode
        try:
            self.screen = sdl2.SDL_CreateWindow(b"window title",
                                                sdl2.SDL_WINDOWPOS_CENTERED,
                                                sdl2.SDL_WINDOWPOS_CENTERED,
                                                1366, 768,
                                                sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE)
            if not self.screen:
                print(sdl2.SDL_GetError())
                return -1
        except Exception as e:
            print(e)
            # Video mode can't be set, fall back
            if "video mode" in str(e):
                self.resolution_fallback()
            elif self.opengl:
                # Try to fix "Couldn't find matching GLX visual" error with unsupported samplebuffers
                self.disable_multisamples()


    def set_window_loop(self, callback, target_fps = 30):
        self.callback = callback


    def open_window(self):
        # Do the traditional loop here
        while Game.started:
            self.callback(0.0)

    def app_loop_tick(self):
        """Runs once every frame before any entity code or rendering."""
        pass

    def resolution_fallback(self):
        """ Reset resolution down to the lowest supported and windowed. """
        print("resolution fallback")
        if Game.full_screen:
            self.flags ^= sdl2.SDL_WINDOW_FULLSCREEN
            Game.full_screen = False
        try:
            Game.screen_resolution = Game.lowest_resolution
            self.screen = sdl2.ext.Window("test title", Game.lowest_resolution, flags=self.flags)
        except Exception as e:
            if self.opengl:
                self.disable_multisamples()
            else:
                raise MyrmidonError("Couldn't find a supported video mode.")


    def disable_multisamples(self):
        """ If this system doesn't support samplebuffers and also as a last ditch to get
        a working video mode we'll try disabling them. """
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_MULTISAMPLEBUFFERS, 0)
        sdl2.SDL_GL_SetAttribute(sdl2.SDL_GL_MULTISAMPLESAMPLES, 0)
        print("disable multisample")
        try:
            Game.screen_resolution = Game.screen_resolution
            self.screen = sdl2.ext.Window("test title", Game.screen_resolution, flags=sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE)
        except Exception as e:
            print(e)
            if "video mode" in str(e):
                self.resolution_fallback()
            else:
                raise MyrmidonError("Couldn't find a supported video mode.")


    def Clock(self):
        import pygame
        return pygame.time.Clock()




    def change_resolution(self, resolution):
        sdl2.ext.quit()
        self.__init__()


    def set_title(self, title):
        sdl2.ext.Window.title = title

    class Font(BaseFont):
        loaded_font = None

        def __init__(self, font = None, size = 20):
            self.size = size
            if isinstance(font, str):
                self.filename = font
                self.loaded_font = sdl2.ext.FontManager(self.filename, size=self.size)

            elif font is None:
                self.loaded_font = sdl2.ext.FontManager(None, size=self.size)
            else:
                self.loaded_font = font
