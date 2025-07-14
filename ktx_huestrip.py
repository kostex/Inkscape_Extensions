#!/usr/bin/env python3
import inkex
from lxml import etree
from math import sqrt,floor
from inkex import PathElement, Path, Group, Color,Rectangle
from inkex import colors

def draw_Tile(x, y, width, height, radius, col, name, parent):
    elem = parent.add(Rectangle())
    elem.style = {
        "fill": "#ff0000",
        "stroke": "none",
        "stroke-width": "0.1mm",
        "stroke-linecap": "round",
        "paint-order": "markers-fill-stroke"
    }
    elem.label = f"tile_{name}"
    elem.set("x", x)
    elem.set("y", y)
    elem.set("ry", radius)
    elem.set("width", width)
    elem.set("height", height)
    elem.style['fill'] = col
    return elem

class KTX_HueStrip(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--size_x", type=float, default=0.5)
        pars.add_argument("--size_y", type=float, default=4.0)
        pars.add_argument("--fillet_radius", type=float, default=0.1)
        pars.add_argument("--offset_gap", type=inkex.Boolean, default=False)
        pars.add_argument("--offset_x", type=float, default=0.55)
        pars.add_argument("--satu", type=int, default=128)
        pars.add_argument("--valu", type=int, default=128)
        pars.add_argument("--incr", type=int, default=1)

    def effect(self):
        svg = self.document.getroot()        
        cl = self.svg.get_current_layer()
        x = 0
        y = 0
        posx = 0
        posy = 0
        hue = 0
        satu = self.options.satu
        valu = self.options.valu
        size_x = self.options.size_x
        size_y = self.options.size_y
        offset_x = self.options.offset_x
        offset_gap = self.options.offset_gap
        fillet_radius = self.options.fillet_radius
        incr = self.options.incr
        
        for y in range(1):
            for x in range(floor(255/incr)):
                kleur = Color("#ff0000")
                kleur.hue = hue
                kleur.saturation = satu
                kleur.lightness = valu
                if offset_gap:
                    x1 = x * offset_x
                else:
                    x1 = x * (size_x+offset_x)
                blokje = draw_Tile(self.svg.unittouu(str(x1) + "mm"),
                                   self.svg.unittouu(str(y) + "mm"),
                                   self.svg.unittouu(str(size_x) + "mm"),
                                   self.svg.unittouu(str(size_y) + "mm"),
                                   fillet_radius,
                                   kleur,
                                   str(kleur),
                                   cl)
                hue += incr


if __name__ == "__main__":
    KTX_HueStrip().run()
