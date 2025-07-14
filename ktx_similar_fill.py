#!/usr/bin/env python3
import inkex
from lxml import etree
from math import sqrt
from inkex import PathElement, Path, Group, Color
from inkex import colors

class KTX_Similar_Fill(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--target_color", type=inkex.Color, help="Target color (hex)")
        pars.add_argument("--threshold", type=int, default=10, help="Color similarity threshold (0-255)")
        pars.add_argument("--live_preview", type=inkex.Boolean, default=True, help="Live Preview")
        

    def color_to_hex_plus_alpha(self, color):
        """Convert an inkex.colors.Color to hex string."""
        r, g, b, a = color.to_rgba()
        return "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, round(a * 255))

    def color_to_hex(self, color):
        """Convert an inkex.colors.Color to hex string."""
        r, g, b, a = color.to_rgba()
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def color_alpha(self, color):
        r, g, b, a = color.to_rgba()
        return a


    def color_distance(self, rgba1, rgba2, include_alpha):
        r_diff = rgba1[0] - rgba2[0]
        g_diff = rgba1[1] - rgba2[1]
        b_diff = rgba1[2] - rgba2[2]
        dist = r_diff**2 + g_diff**2 + b_diff**2
        if include_alpha:
            a_diff = rgba1[3] - rgba2[3]
            dist += a_diff**2
        return sqrt(dist)

    def hex_to_rgba(self, col):
        return f"rgba({Color(col).red},{Color(col).green},{Color(col).blue},1)"

    def col_distance(self, source, target):
        r_diff = source.red - target.red
        g_diff = source.green - target.green
        b_diff = source.blue - target.blue
        a_diff = source.alpha - target.alpha
        dist = r_diff**2 + g_diff**2 + b_diff**2 + a_diff**2
        return sqrt(dist)

    def effect(self):
        svg = self.document.getroot()
        document = self.svg.xpath('//svg:*', namespaces=inkex.NSS)
        
        target_rgba = self.options.target_color
        target_hex = self.color_to_hex(self.options.target_color)
        threshold = self.options.threshold
        preview = self.options.live_preview

        matched = []

        if len(svg.selection) == 0:
            looper = document
        else:
            looper = svg.selection

        for element in looper:
            tag = element.tag.split('}')[-1]
            if tag in ['svg', 'defs']:
                continue
            id_attr = element.get('id', 'no-id')
            style = element.style if hasattr(element, 'style') else 'no-style'
            attribs = dict(element.attrib)
            # self.msg(f"{self.hex_to_rgba(element.style.get('fill'))}")
            # self.msg(f"{Color(element.style.get('fill')).red}")
            distance = self.col_distance(Color(element.style.get('fill')), self.options.target_color)
            # self.msg(f"{distance}")
            if distance <= threshold:
                element.style["fill"] = target_hex # "#ff0000"
                # element.style["opacity"] = self.color_alpha(self.options.target_color) # "0.5"
                matched.append(element)
            else:
                if preview:
                    # element.style["fill"] = "#000000"
                    element.style["opacity"] = "0"
                
            # self.msg(f"Element: {tag}")
            # self.msg(f"  ID: {id_attr}")
            # self.msg(f"  Style: {style}")
            # self.msg(f"  Attributes: {attribs}")
            # self.msg("-" * 40)

        group = Group()
        group.label = target_hex
        self.svg.get_current_layer().add(group)
        for elem in matched:
            group.add(elem)

if __name__ == "__main__":
    KTX_Similar_Fill().run()
