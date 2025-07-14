#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2024 Roel Koster
#
"""
Provide the Scrabble Tiles
"""
import os
import random
import string
import inkex
from inkex import etree
from inkex import Rectangle, TextElement, PathElement, Circle
from inkex.elements import Group
from tempfile import TemporaryDirectory

TEXT_TEMPLATE = "dominant-baseline: middle;fill: #000000;font-size: %f;font-family: %s;font-weight: %s;-inkscape-font-specification: %s;line-height: 1;paint-order: markers fill stroke;stroke: none;stroke-dasharray: none;stroke-linecap: round;stroke-width: 0.1mm;text-anchor: middle;"


def draw_Character(font_size, font_family, font_bold, character, parent):
    elem = parent.add(TextElement())
    font_weight = "bold" if font_bold else "normal"
    elem.set("style", TEXT_TEMPLATE % (font_size, font_family, font_weight, font_family))
    elem.text = str(character)
    elem.label = f"characters_{character}"
    return elem


def run_inkscape_and_replace_svg(svg, action_str):
    '''Invoke a set of actions in a child Inkscape then replace the current
    SVG contents with those of the child Inkscape.'''

    with TemporaryDirectory(prefix='inkscape-command-') as tmpdir:
        svg_file = inkex.command.write_svg(svg, tmpdir, 'input.svg')

        cwd = os.getcwd()
        os.chdir(os.path.dirname(svg_file))

        args = ['--batch-process']
        if action_str[0].strip().islower():
            instance_tag = ''.join(random.choices(string.ascii_letters, k=10))
            args.append(f'--app-id-tag={instance_tag}')
        inkex.command.inkscape(svg_file,
                               *args,
                               actions=action_str)
        os.chdir(cwd)
        for element in svg:
            svg.remove(element)
        append_tree = etree.parse(svg_file)
        for element in append_tree.getroot():
            svg.append(element)


class KTXTextArray(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--start_x", type=float, default=0.0)
        pars.add_argument("--start_y", type=float, default=0.0)
        pars.add_argument("--offset_x", type=float, default=40.0)
        pars.add_argument("--offset_y", type=float, default=40.0)
        pars.add_argument("--text", default="Hello\nWorld")
        pars.add_argument("--text_font_size", type=float, default=11.0)
        pars.add_argument("--text_font_family", default="Interstate")
        pars.add_argument("--text_font_bold", type=inkex.Boolean, default=False)
        pars.add_argument("--enable_merge", type=inkex.Boolean, default=False)

    def effect(self):
        svg = self.document.getroot()

        groups = {
            'Text': Group(),
            'Specials': Group()
        }

        action_chunks = []
        text_list = []

        cl = self.svg.get_current_layer()

        x = self.options.start_x
        y = self.options.start_y

        offset_x = self.options.offset_x
        offset_y = self.options.offset_y

        text = self.options.text
        text_font_size = self.options.text_font_size
        text_font_family = self.options.text_font_family
        text_font_bold = self.options.text_font_bold

        enable_merge = self.options.enable_merge

        text = text.replace("\\n", ";")
        text = text.replace(" ", "_")
        for character in text:
            if character == ';':  # new line
                y += offset_y
                x = self.options.start_x
            else:
                text = draw_Character(text_font_size,
                                        text_font_family,
                                        text_font_bold,
                                        character,
                                        cl)
                text.set("x", self.svg.unittouu(str(x) + "mm"))
                text.set("y", self.svg.unittouu(str(y) + "mm"))
                if character != '_':
                    if enable_merge:
                        text_list.append(text.get_id())
                    else:
                        groups['Text'].add(text)
                else:
                    groups['Specials'].add(text)


                x += offset_x

        if enable_merge:
            action_chunks.extend(['select-by-id:' + obj_id for obj_id in text_list])
            action_chunks.extend(['path-union'])
            action_chunks.extend(['select-clear'])

            action_chunks.extend(['select-by-id:' + text_list[0]])
            action_chunks.extend(['object-set-attribute:inkscape:label, Text'])
            action_chunks.extend(['select-clear'])
            action_chunks.extend(['export-filename:input.svg',
                                  'export-overwrite',
                                  'export-do',
                                  'quit-immediate'])
            action_str = ';'.join(action_chunks)
            run_inkscape_and_replace_svg(svg, action_str)
        else:
            for group_name, group in groups.items():
                if len(group) > 0:
                    group.label = f"{group_name}"
                    self.svg.add(group)


if __name__ == "__main__":
    KTXTextArray().run()
