#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2025 Roel Koster
#
"""
Lets array a bunch of objects
"""

import inkex
from inkex import etree
from inkex import transforms
from math import floor

class KTXObjectArray(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--offset_x", type=float, default=40.0)
        pars.add_argument("--offset_y", type=float, default=40.0)
        pars.add_argument("--num_x", type=int, default=4)
        pars.add_argument("--num_y", type=int, default=4)

    def effect(self):
        svg = self.document.getroot()

        offset_x = self.options.offset_x
        offset_y = self.options.offset_y

        num_x = self.options.num_x
        num_y = self.options.num_y

        for node in self.svg.selection:
            if node is not None:
                pos_x = node.get('x')
                pos_y = node.get('y')
                for i in range(num_x):
                    for j in range(num_y):
                        if i == 0 and j == 0:
                            continue  # Skip original object
                        new_node = etree.Element(node.tag, node.attrib)
                        new_node.set("x", f"{float(pos_x)+(i * offset_x)}")
                        new_node.set("y", f"{float(pos_y)+(j * offset_y)}")
                        node.getparent().append(new_node)

if __name__ == "__main__":
    KTXObjectArray().run()
