#!/usr/bin/env python3
# coding=utf-8
#
# Copyright (C) 2025 Roel Koster
#
"""
Provide the Watch Numbers
"""
import os
import math
import random
import string
import inkex
from inkex import etree
from inkex import TextElement, PathElement, Circle
from inkex.elements import Group
from tempfile import TemporaryDirectory
from inkex.localization import (
    inkex_gettext as _,
    inkex_fgettext as _f,
    inkex_pgettext as pgettext,
)

TEXT_TEMPLATE = "dominant-baseline: middle;fill: #000000;font-size: %fmm;font-family: %s;font-weight: %s;-inkscape-font-specification: %s;line-height: 1;paint-order: markers fill stroke;stroke: none;stroke-dasharray: none;stroke-linecap: round;stroke-width: 0.1mm;text-anchor: middle;"

def polar(angle_degrees, distance):
    # Convert angle from degrees to radians
    angle_radians = math.radians(angle_degrees)
    
    # Calculate x and y coordinates
    x = distance * math.cos(angle_radians)
    y = distance * math.sin(angle_radians)
    
    return x, y


def draw_CharValueRotated(x, y, font_size, font_family, font_bold, character, angle, parent):
    elem = parent.add(TextElement())
    font_weight = "bold" if font_bold else "normal"
    elem.set("style", TEXT_TEMPLATE % (font_size, font_family, font_weight, font_family))
    elem.text = character
    elem.set("x", x)
    elem.set("y", y)
    elem.label = f"values_{character}"
    elem.transform = inkex.Transform(f"rotate({angle},{x},{y})")
    return elem

def draw_CharValue(x, y, font_size, font_family, font_bold, character, parent):
    elem = parent.add(TextElement())
    font_weight = "bold" if font_bold else "normal"
    elem.set("style", TEXT_TEMPLATE % (font_size, font_family, font_weight, font_family))
    elem.text = character
    elem.set("x", x)
    elem.set("y", y)
    elem.label = f"values_{character}"
    return elem

def draw_Line(x1, y1, x2, y2, name, parent):
    path_data = f"M {x1},{y1} L {x2},{y2}"
    elem = parent.add(PathElement(d=path_data, style="stroke:red;stroke-width:1;stroke-linecap:round"))
    elem.label = f"line_{name}"
    return elem

def draw_Dot(x, y, radius, name, parent):
    elem = parent.add(Circle())
    elem.style = {
        "stroke": "#000000",
        "stroke-width": "0.1mm",
        "fill": "none",
        "stroke-linecap": "round",
        "paint-order": "markers-fill-stroke"
    }
    elem.label = f"dots_{name}"
    elem.set("cx", x)
    elem.set("cy", y)
    elem.set("r", radius)
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


class KTXWatchNumbers(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--start_x", type=float, default=0.0)
        pars.add_argument("--start_y", type=float, default=0.0)
        pars.add_argument("--radius", type=float, default=40.0)

        pars.add_argument("--num_items", type=int, default=12)
        pars.add_argument("--start_angle", type=float, default=90.0)
        pars.add_argument("--start_number", type=int, default=1)
        pars.add_argument("--inc_number", type=int, default=1)
        pars.add_argument("--inc_angle", type=float, default=30.0)
        pars.add_argument("--rotate", type=inkex.Boolean, default=False)
        pars.add_argument("--readable", type=inkex.Boolean, default=False)
        pars.add_argument("--add_angle", type=float, default=0.0)

        pars.add_argument("--text_font_size", type=float, default=11.0)
        pars.add_argument("--text_font_family", default="Interstate")
        pars.add_argument("--text_font_bold", type=inkex.Boolean, default=False)

        pars.add_argument("--mark_center", type=inkex.Boolean, default=True)

        pars.add_argument("--enable_merge", type=inkex.Boolean, default=False)

    def effect(self):
#       self.msg(pgettext("Message", tile))
        svg = self.document.getroot()

        groups = {
            'Values': Group(),
        }

        action_chunks = []
        values_list = []

        cl = self.svg.get_current_layer()

        x = self.options.start_x
        y = self.options.start_y
        radius = self.options.radius

        num_items = self.options.num_items
        start_angle = self.options.start_angle
        start_number = self.options.start_number
        inc_number = self.options.inc_number
        inc_angle = self.options.inc_angle
        rotate = self.options.rotate
        add_angle = self.options.add_angle
        readable = self.options.readable
        mark_center = self.options.mark_center

        text_font_size = self.options.text_font_size
        text_font_family = self.options.text_font_family
        text_font_bold = self.options.text_font_bold

        enable_merge = self.options.enable_merge

        angle = start_angle
        curnum = start_number
        if rotate:
            for item in range(num_items):
                angle += inc_angle
                if readable:
                    if angle > 0.0 and angle < 180.0:
                        rota = angle-180.0
                    else:
                        rota = angle
                else:
                    rota = angle
                cvalue = draw_CharValueRotated(self.svg.unittouu(str(x + polar(angle,radius)[0]) + "mm"),
                                        self.svg.unittouu(str(y + polar(angle,radius)[1]) + "mm"),
                                        text_font_size,
                                        text_font_family,
                                        text_font_bold,
                                        str(curnum),
                                        rota+add_angle,
                                        cl)
                curnum += inc_number

                if enable_merge:
                    values_list.append(cvalue.get_id())
                else:
                    groups['Values'].add(cvalue)
        else:
            for item in range(num_items):
                angle += inc_angle
                cvalue = draw_CharValue(self.svg.unittouu(str(x + polar(angle,radius)[0]) + "mm"),
                                        self.svg.unittouu(str(y + polar(angle,radius)[1]) + "mm"),
                                        text_font_size,
                                        text_font_family,
                                        text_font_bold,
                                        str(curnum),
                                        cl)
                curnum += inc_number

                if enable_merge:
                    values_list.append(cvalue.get_id())
                else:
                    groups['Values'].add(cvalue)

        if mark_center:
            cn = draw_Dot(self.svg.unittouu(str(x) + "mm"),
                          self.svg.unittouu(str(y) + "mm"),
                          self.svg.unittouu("2mm"),
                          "center",
                          cl)
            if enable_merge:
                values_list.append(cn.get_id())
            else:
                groups['Values'].add(cn)

        if enable_merge:
            action_chunks.extend(['select-by-id:' + obj_id for obj_id in values_list])
            action_chunks.extend(['path-union'])
            action_chunks.extend(['select-clear'])

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
    KTXWatchNumbers().run()
