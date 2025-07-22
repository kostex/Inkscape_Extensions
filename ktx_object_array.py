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
from inkex import Transform

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

        original_selection = list(self.svg.selected.values())

        for original_element in original_selection:
            original_transform_matrix = original_element.transform.matrix

            for i in range(num_x):
                for j in range(num_y):
                    if i == 0 and j == 0:
                        continue # Skip the original object itself

                    duplicate_element = inkex.etree.fromstring(inkex.etree.tostring(original_element))
                    current_transform_str = duplicate_element.get('transform')
                    if current_transform_str:
                        current_transform = Transform(current_transform_str)
                    else:
                        current_transform = Transform()
                    translation_transform = Transform(f"translate({i * offset_x},{j * offset_y})")
                    new_transform = current_transform @ translation_transform
                    duplicate_element.set('transform', str(new_transform))
                    original_element.getparent().append(duplicate_element)

if __name__ == "__main__":
    KTXObjectArray().run()
