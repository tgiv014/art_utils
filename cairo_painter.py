# This file builds a class that generalizes line drawing in cairo
# It's purpose is to simplify the structure of generative art scripts
# that use cairo to paint.

import numpy as np
import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango
from gi.repository import PangoCairo

class CairoPainter:
    def __init__(self, path='./frames/out{}.png', width=1920, height=1080, bg=None, mode='image'):
        self.width, self.height = width, height
        self.path = path
        self.mode = mode
        if self.mode == 'svg':
            self.surface = cairo.SVGSurface(path, width, height)
        else:
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            
        self.ctx = cairo.Context(self.surface)
        if bg is not None and len(bg) not in [3,4]:
            raise Exception('background color is not formatted correctly')

        if bg is not None:
            self.ctx.rectangle(0, 0, self.width, self.height)
            alpha = bg[3] if len(bg)==4 else 1
            self.ctx.set_source_rgba(bg[0],bg[1],bg[2],alpha)
            self.ctx.fill()
        
        self.frame = 0
    
    # Adjust the coordinate frame such that all draws happen within an offset
    # from the image borders
    def insert_borders(self, x, y):
        self.ctx.translate(x,y)
        self.ctx.scale((self.width-2*x)/self.width,(self.height-2*y)/self.height)
    
    def draw_line(self, line_pts, color=[1,1,1], width=1, cap=cairo.LineCap.ROUND):
        self.ctx.move_to(line_pts[0,0],line_pts[0,1])
        for pt in line_pts:
            self.ctx.line_to(pt[0],pt[1])
        self.ctx.set_line_width(width)
        self.ctx.set_line_cap(cap)
        alpha = color[3] if len(color)==4 else 1
        self.ctx.set_source_rgba(color[0],color[1],color[2],alpha) #2c3e50
        self.ctx.stroke()
    
    def draw_circle(self, pt, color=[1,1,1], r=1):
        self.ctx.arc(pt[0], pt[1], r, 0, 2 * np.pi)
        alpha = color[3] if len(color)==4 else 1
        self.ctx.set_source_rgba(color[0],color[1],color[2],alpha) #2c3e50
        self.ctx.fill()
    
    def draw_text(self, text, x, y, color=[1,1,1], size=36):
        self.layout = PangoCairo.create_layout(self.ctx)
        self.layout.set_font_description(Pango.font_description_from_string('Inter Extra-Bold {}'.format(size)))
        self.layout.set_alignment(Pango.Alignment.CENTER)
        self.layout.set_markup(text, -1)
        _, extents = self.layout.get_pixel_extents()
        tw, th = extents.width, extents.height
        self.ctx.move_to(x - tw/2, y - th/2)
        alpha = color[3] if len(color)==4 else 1
        self.ctx.set_source_rgba(color[0],color[1],color[2],alpha) #2c3e50
        PangoCairo.show_layout(self.ctx, self.layout)
        return [[x-tw/2,y-th/2],[x+tw/2,y+th/2]]
    
    def get_pixel(self, x, y):
        if self.mode == 'svg':
            raise Exception('image sampling unsupported in svg mode')
        x = int(x)
        y = int(y)
        if x < 0 or x >= self.width:
            return 0,0,0,0
        if y < 0 or y >= self.height:
            return 0,0,0,0
        
        data = self.surface.get_data()
        stride = self.surface.get_stride()
        index = y*stride + 4*x
        pixel = data[index:index+4]
        r,g,b,a = pixel[0],pixel[1],pixel[2],pixel[3]
        return r,g,b,a

    def pixel_filled(self, x, y):
        # use alpha channel to check
        return self.get_pixel(x, y)[3] != 0
    
    def output_frame(self):
        if self.mode == 'svg':
            raise Exception('Animation not supported in SVG mode')
        self.surface.write_to_png(self.path.format(self.frame))
        self.frame += 1
    
    def output_snapshot(self, path=None):
        if path is None:
            path = self.path
        if self.mode == 'svg':
            self.surface.show_page()
        else:
            self.surface.write_to_png(path)

if __name__ == '__main__':
    imgpainter = CairoPainter()
    imgpainter.insert_borders(40,40)
    imgpainter.draw_line(np.array([[0,0],[1920,1080]]), color=[1,0,0], width=20)
    imgpainter.draw_circle(np.array([1920/2,1080/2]), r=100)
    imgpainter.draw_text('Test', 1920/2, 1080/2, color=[0.5,0.5,0.5], size=600)
    imgpainter.get_pixel(1920/2, 1080/2)
    print(imgpainter.pixel_filled(1920/2,1080/2))
    print(imgpainter.pixel_filled(0,0))
    print(imgpainter.pixel_filled(1920-1,1080-1))
    imgpainter.output_snapshot()

    svgpainter = CairoPainter('./out.svg', mode='svg')
    svgpainter.insert_borders(40, 40)
    svgpainter.draw_line(np.array([[0,0],[1920,1080]]), color=[1,0,0], width=20)
    svgpainter.draw_circle(np.array([1920/2,1080/2]), r=100)
    svgpainter.draw_text('Test', 1920/2, 1080/2, color=[0.5,0.5,0.5], size=600)
    svgpainter.output_snapshot()