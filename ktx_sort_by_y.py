#!/usr/bin/env python3
# (c)2025 Koelooptiemanna Productions

import inkex
from lxml import etree


class KTX_Sort_By_Y(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--satu", type=int, help="Saturation")
        pars.add_argument("--valu", type=int, help="Value")

    def effect(self):
        svg = self.document.getroot()
        document = self.svg.xpath('//svg:*', namespaces=inkex.NSS)
        number_of_selected_objects = len(svg.selection)
        vb = svg.get('viewBox').split(' ')
        xh = float(vb[2])/2.0
        elems = []
        looper = svg.selection if number_of_selected_objects > 0 else document
        for elem in looper:
            tag = elem.tag.split('}')[-1]
            if tag in ['svg', 'defs','g']:
               continue
            posy = float(elem.get('y'))
            elems.append([posy,elem])
            svg.remove(elem)
        elems = sorted(elems, key=lambda x:x[0], reverse=True)
        # self.msg(f"{elems}")
        for element in elems:
            svg.append(element[1])

if __name__ == "__main__":
    KTX_Sort_By_Y().run()
