#!/usr/bin/env python3
# (c)2025 Koelooptiemanna Productions

import inkex
from lxml import etree


class KTX_Test(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--satu", type=int, help="Saturation")
        pars.add_argument("--valu", type=int, help="Value")

    def effect(self):
        svg = self.document.getroot()
        document = self.svg.xpath('//svg:*', namespaces=inkex.NSS)
        looper = svg.selection if len(svg.selection) > 0 else document
        for elem in looper:
            tag = elem.tag.split('}')[-1]
            if tag in ['svg', 'defs','g']:
               continue
            self.msg(f"{elem.style.get('fill')}")

if __name__ == "__main__":
    KTX_Test().run()
