#!/usr/bin/env python3
import inkex
from lxml import etree
from math import floor
from inkex import Color


class KTX_RandomFillColor(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--satu", type=int, help="Saturation")
        pars.add_argument("--valu", type=int, help="Value")

    def effect(self):
        svg = self.document.getroot()        
        document = self.svg.xpath('//svg:*', namespaces=inkex.NSS)
        number_of_selected_objects = len(svg.selection)
        satu = self.options.satu
        valu = self.options.valu
        hue = 0
        if number_of_selected_objects > 0:
            incr = floor(255/number_of_selected_objects)
            for elem in svg.selection:
                col = Color("#ff0000")
                col.hue = hue
                col.saturation = satu
                col.lightness = valu
                elem.style['fill'] = col
                hue+=incr
        else:
            self.msg(f"Select some objects, dumbass!")


if __name__ == "__main__":
    KTX_RandomFillColor().run()
