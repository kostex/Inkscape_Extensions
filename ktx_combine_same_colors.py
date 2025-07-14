#!/usr/bin/env python3
import inkex
import os
import random
import string
from lxml import etree
from math import sqrt
from inkex import PathElement, Path, Group, Color
from inkex import colors
from tempfile import TemporaryDirectory

def hsl(color):
    r = int(color[1:3]) / 255
    g = int(color[3:5]) / 255
    b = int(color[5:7]) / 255

    minimum = min(r, min(g, b))
    maximum = max(r, max(g, b))
    delta = max - min
    l = (min + max) / 2

    s = 0
    if l > 0 and l < 1:
      s = delta / (2 * l if l < 0.5 else 2 - 2 * l)

    h = 0
    if delta > 0:
      if max == r and max != g:
          h += (g - b) / delta
      if max == g and max != b:
          h += (2 + (b - r) / delta)
      if max == b and max != r:
          h += (4 + (r - g) / delta)
      h /= 6
    return [h * 255,s * 255,l * 255];

def rgb(color):
    return [int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)]

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

class KTX_Combine_Same_Colors(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--group_only", type=inkex.Boolean, default=True, help="Live Preview")

    def effect(self):
        svg = self.document.getroot()
        document = self.svg.xpath('//svg:*', namespaces=inkex.NSS)
        
        group_only = self.options.group_only

        matched = []

        for element in document:
            tag = element.tag.split('}')[-1]
            if tag in ['svg', 'defs']:
                continue
            attr_id = element.get('id', 'no-id')
            style = element.style if hasattr(element, 'style') else 'no-style'
            fill = element.style.get('fill')
            # self.msg(f"{fill}")
            fill_found = False
            for f in matched:
                if f[0] == fill:
                    fill_found = True
                    f.append([attr_id,element])
                    break
            if not fill_found:
                matched.append([fill, [attr_id,element]])

        if group_only:
            for f in matched:
                group = Group()
                group.label = f[0]
                self.svg.add(group)
                for elem in f[1:]:
                    group.add(elem[1])
        else:
            action_chunks = []
            for f in matched:
            # action_chunks.extend(['select-by-id:' + obj_id for obj_id in tiles_list])
                action_chunks.extend(['select-by-id:' + elem[0] for elem in f[1:]])
                action_chunks.extend(['object-to-path'])
                action_chunks.extend(['path-combine'])
                action_chunks.extend(['select-clear'])

            action_chunks.extend(['export-filename:input.svg',
                                  'export-overwrite',
                                  'export-do',
                                  'quit-immediate'])
            action_str = ';'.join(action_chunks)
            run_inkscape_and_replace_svg(svg, action_str)
            

        
        # g = Group()
        # self.svg.add(g)
        # g.label = "Kut"
        # for element in document:
            # tag = element.tag.split('}')[-1]
            # if tag == 'g':
                # #self.msg(f"{element.label}")
                # if element.label[1] == 'f':
                    # g.add(element)


if __name__ == "__main__":
    KTX_Combine_Same_Colors().run()


# self.msg(f"{self.hex_to_rgba(element.style.get('fill'))}")
# self.msg(f"{Color(element.style.get('fill')).red}")
# distance = self.col_distance(Color(element.style.get('fill')), self.options.target_color)
# self.msg(f"{distance}")

# if distance <= threshold:
    # element.style["fill"] = target_hex # "#ff0000"
    # st = Color(element.style.get('fill'))
    # # element.style["opacity"] = self.color_alpha(self.options.target_color) # "0.5"
# else:
    # if preview:
        # # element.style["fill"] = "#000000"
        # element.style["opacity"] = "0"
    
# self.msg(f"Element: {tag}")
# self.msg(f"  ID: {id_attr}")
# self.msg(f"  Style: {style}")
# self.msg(f"  Attributes: {attribs}")
# self.msg("-" * 40)
#self.msg(f"Lijst: {matched}")
# group = Group()
# group.label = target_hex
# self.svg.get_current_layer().add(group)
# for elem in matched:
# group.add(matched[1])
# self.msg(f"{unique}")