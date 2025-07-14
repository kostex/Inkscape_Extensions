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
from inkex import Rectangle, TextElement, PathElement, Circle, Line
from inkex.elements import Group
from tempfile import TemporaryDirectory
from inkex.localization import (
    inkex_gettext as _,
    inkex_fgettext as _f,
    inkex_pgettext as pgettext,
)

TEXT_TEMPLATE = "dominant-baseline: middle;fill: #000000;font-size: %fmm;font-family: %s;font-weight: %s;-inkscape-font-specification: %s;line-height: 1;paint-order: markers fill stroke;stroke: none;stroke-dasharray: none;stroke-linecap: round;stroke-width: 0.03mm;text-anchor: middle;"


def draw_Tile(x, y, size, radius, name, parent):
    elem = parent.add(Rectangle())
    elem.style = {
        "fill": "none",
        "stroke": "#000000",
        "stroke-width": "0.03mm",
        "stroke-linecap": "round",
        "paint-order": "markers-fill-stroke"
    }
    elem.label = f"tile_{name}"
    elem.set("x", x)
    elem.set("y", y)
    elem.set("ry", radius)
    elem.set("width", size)
    elem.set("height", size)
    return elem


def draw_Character(font_size, font_family, font_bold, character, parent):
    elem = parent.add(TextElement())
    font_weight = "bold" if font_bold else "normal"
    elem.set("style", TEXT_TEMPLATE % (font_size, font_family, font_weight, font_family))
    elem.text = str(character)
    elem.label = f"characters_{character}"
    return elem


def draw_Line(x1, y1, x2, y2, name, parent):
    path_data = f"M {x1},{y1} L {x2},{y2}"
    elem = parent.add(PathElement(d=path_data, style="stroke:red;stroke-width:0.1mm;stroke-linecap:round"))
    elem.label = f"line_{name}"
    return elem


def draw_Dot(x, y, radius, name, parent):
    elem = parent.add(Circle())
    elem.style = {
        "stroke": "none",
        "stroke-width": "0.03mm",
        "fill": "#000000",
        "stroke-linecap": "round",
        "paint-order": "markers-fill-stroke"
    }
    elem.label = f"dots_{name}"
    elem.set("cx", x)
    elem.set("cy", y)
    elem.set("r", radius)
    return elem


def scrabble_value(letter):
    letter_values = {
        'a': '1', 'b': '3', 'c': '3', 'd': '2', 'e': '1', 'f': '4', 'g': '2', 'h': '4', 'i': '1',
        'j': '8', 'k': '5', 'l': '1', 'm': '3', 'n': '1', 'o': '1', 'p': '3', 'q': '10', 'r': '1',
        's': '1', 't': '1', 'u': '1', 'v': '4', 'w': '4', 'x': '8', 'y': '4', 'z': '10', ' ': ''
    }
    letter = letter.lower()
    return letter_values.get(letter, '1')


def draw_CharValue(x, y, font_size, font_family, font_bold, character, parent):
    elem = parent.add(TextElement())
    font_weight = "bold" if font_bold else "normal"
    elem.set("style", TEXT_TEMPLATE % (font_size, font_family, font_weight, font_family))
    elem.text = scrabble_value(character)
    elem.set("x", x)
    elem.set("y", y)
    elem.label = f"values_{character}"
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


class KTXScrabbleTiles(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--start_x", type=float, default=0.0)
        pars.add_argument("--start_y", type=float, default=0.0)
        pars.add_argument("--text", default="Hello World")
        pars.add_argument("--text_font_size", type=float, default=11.0)
        pars.add_argument("--text_font_family", default="Interstate")
        pars.add_argument("--text_font_bold", type=inkex.Boolean, default=False)
        pars.add_argument("--char_offset", type=float, default=-0.350)
        pars.add_argument("--tile_size", type=float, default=15.0)
        pars.add_argument("--tile_cornerradius", type=float, default=2.0)
        pars.add_argument("--enable_dots", type=inkex.Boolean, default=False)
        pars.add_argument("--dot_diameter", type=float, default=1.0)
        pars.add_argument("--enable_scrabblevalue", type=inkex.Boolean, default=False)
        pars.add_argument("--scrabblevalue_font_size", type=float, default=4.0)
        pars.add_argument("--scrabblevalue_font_family", default="Arial")
        pars.add_argument("--scrabblevalue_font_bold", type=inkex.Boolean, default=False)
        pars.add_argument("--scrabblevalue_offset", type=float, default=1.5)
        pars.add_argument("--enable_merge", type=inkex.Boolean, default=False)

    def effect(self):
#       self.msg(pgettext("Message", tile))
        svg = self.document.getroot()

        groups = {
            'Tiles': Group(),
            'Lines': Group(),
            'Text': Group(),
            'Dots': Group(),
            'Values': Group(),
            'Specials': Group()
        }

        action_chunks = []
        tiles_list = []
        text_list = []
        lines_list = []
        dots_list = []
        values_list = []

        cl = self.svg.get_current_layer()

        x = self.options.start_x
        y = self.options.start_y

        text = self.options.text
        text_font_size = self.svg.unittouu(str(self.options.text_font_size))
        text_font_family = self.options.text_font_family
        text_font_bold = self.options.text_font_bold
        char_offset = self.options.char_offset

        tile_size = self.options.tile_size
        tile_size_mm = self.svg.unittouu(str(self.options.tile_size) + "mm")
        tile_cornerradius = self.options.tile_cornerradius
        tile_cornerradius_mm = self.svg.unittouu(str(self.options.tile_cornerradius) + "mm")

        enable_dots = self.options.enable_dots
        dot_radius_mm = self.svg.unittouu(str(self.options.dot_diameter/2) + "mm")

        enable_scrabblevalue = self.options.enable_scrabblevalue
        scrabblevalue_font_size = self.svg.unittouu(str(self.options.scrabblevalue_font_size))
        scrabblevalue_font_family = self.options.scrabblevalue_font_family
        scrabblevalue_font_bold = self.options.scrabblevalue_font_bold
        scrabblevalue_offset = self.options.scrabblevalue_offset

        enable_merge = self.options.enable_merge

        xcount = 0
        xcount_old = 0
        text = text.replace("\\n", ";")
        text = text.replace(" ", "_")
        for character in text:
            if character == ';':  # new line
                y += tile_size
                x = self.options.start_x
                xcount_old = xcount
                xcount = 0
            else:
                tile = draw_Tile(self.svg.unittouu(str(x) + "mm"),
                                 self.svg.unittouu(str(y) + "mm"),
                                 tile_size_mm,
                                 tile_cornerradius_mm,
                                 character,
                                 cl)
                if enable_merge:
                    tiles_list.append(tile.get_id())
                else:
                    groups['Tiles'].add(tile)

                text = draw_Character(text_font_size,
                                        text_font_family,
                                        text_font_bold,
                                        character,
                                        cl)
                text.set("x", self.svg.unittouu(str(x + (tile_size/2)) + "mm"))
                text.set("y", self.svg.unittouu(str(y + (tile_size/2) - char_offset) + "mm"))
                if character != '_':
                    if enable_merge:
                        text_list.append(text.get_id())
                    else:
                        groups['Text'].add(text)
                else:
                    groups['Specials'].add(text)


                if not x == 0:
                    vl = draw_Line(self.svg.unittouu(str(x) + "mm"),
                                   self.svg.unittouu(str(y + tile_cornerradius) + "mm"),
                                   self.svg.unittouu(str(x) + "mm"),
                                   self.svg.unittouu(str(y + tile_size - tile_cornerradius) + "mm"),
                                   character,
                                   cl)
                    if enable_merge:
                        lines_list.append(vl.get_id())
                    else:
                        groups['Lines'].add(vl)

                xcount += 1
                if xcount <= xcount_old:
                    hl = draw_Line(self.svg.unittouu(str(x + tile_cornerradius) + "mm"),
                                   self.svg.unittouu(str(y) + "mm"),
                                   self.svg.unittouu(str(x + tile_size - tile_cornerradius) + "mm"),
                                   self.svg.unittouu(str(y) + "mm"),
                                   character,
                                   cl)
                    if enable_merge:
                        lines_list.append(hl.get_id())
                    else:
                        groups['Lines'].add(hl)

                if enable_dots:
                    dot = draw_Dot(self.svg.unittouu(str(x + tile_size - tile_cornerradius) + "mm"),
                                   self.svg.unittouu(str(y + tile_size - tile_cornerradius) + "mm"),
                                   dot_radius_mm,
                                   character,
                                   cl)
                    if enable_merge:
                        dots_list.append(dot.get_id())
                    else:
                        groups['Dots'].add(dot)

                if enable_scrabblevalue:
                    cvalue = draw_CharValue(self.svg.unittouu(str(x + tile_size - tile_cornerradius - scrabblevalue_offset) + "mm"),
                                            self.svg.unittouu(str(y + tile_size - tile_cornerradius - scrabblevalue_offset) + "mm"),
                                            scrabblevalue_font_size,
                                            scrabblevalue_font_family,
                                            scrabblevalue_font_bold,
                                            character,
                                            cl)
                    if enable_merge:
                        values_list.append(cvalue.get_id())
                    else:
                        groups['Values'].add(cvalue)

                x += tile_size

        if enable_merge:
            action_chunks.extend(['select-by-id:' + obj_id for obj_id in tiles_list])
            action_chunks.extend(['object-to-path'])
            action_chunks.extend(['path-union'])
            action_chunks.extend(['select-clear'])
            action_chunks.extend(['select-by-id:' + obj_id for obj_id in text_list])
            action_chunks.extend(['path-union'])
            action_chunks.extend(['select-clear'])
            action_chunks.extend(['select-by-id:' + obj_id for obj_id in lines_list])
            action_chunks.extend(['path-combine'])
            action_chunks.extend(['select-clear'])
            if enable_dots:
                action_chunks.extend(['select-by-id:' + obj_id for obj_id in dots_list])
                action_chunks.extend(['path-union'])
                action_chunks.extend(['select-clear'])
            if enable_scrabblevalue:
                action_chunks.extend(['select-by-id:' + obj_id for obj_id in values_list])
                action_chunks.extend(['path-union'])
                action_chunks.extend(['select-clear'])

            action_chunks.extend(['select-by-id:' + tiles_list[0]])
            action_chunks.extend(['object-set-attribute:inkscape:label, Outline'])
            action_chunks.extend(['select-clear'])
            action_chunks.extend(['select-by-id:' + text_list[0]])
            action_chunks.extend(['object-set-attribute:inkscape:label, Text'])
            action_chunks.extend(['select-clear'])
            action_chunks.extend(['select-by-id:' + lines_list[-1]])
            action_chunks.extend(['object-set-attribute:inkscape:label, Lines'])
            action_chunks.extend(['select-clear'])
            if enable_dots:
                action_chunks.extend(['select-by-id:' + dots_list[0]])
                action_chunks.extend(['object-set-attribute:inkscape:label, Dots'])
                action_chunks.extend(['select-clear'])
            if enable_scrabblevalue:
                action_chunks.extend(['select-by-id:' + values_list[0]])
                action_chunks.extend(['object-set-attribute:inkscape:label, Values'])
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
    KTXScrabbleTiles().run()
