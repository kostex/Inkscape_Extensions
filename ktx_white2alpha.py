#!/usr/bin/env python3
import inkex
from PIL import Image
from io import BytesIO
import base64


def avg(a):
    return int(sum(a)/len(a))

class KTX_White2Alpha(inkex.EffectExtension):
    """
    Replaces white in selected embedded images with transparency.
    """

    def add_arguments(self, pars):
        pars.add_argument("--threshold", type=int, default=15)
        pars.add_argument("--mode", type=int, default=1)

    def effect(self):
        threshold = self.options.threshold
        mode = self.options.mode
        selected_images = self.svg.selected.values()
        if not selected_images:
            inkex.errormsg("Please select one or more images.")
            return

        for image_id, image_element in self.svg.selected.items():
#           inkex.utils.debug(image_element)
            if image_element is None or str(image_element) != 'image':
                inkex.errormsg(f"Object with id '{image_id}' is not an image. Skipping.")
                continue

            href = image_element.get('xlink:href')
            if not href.startswith('data:image/'):
                inkex.errormsg(f"Image with id '{image_id}' is not embedded. Skipping.")
                continue

            metadata, base64_data = href.split(',', 1)
            image_format = metadata.split(';')[0].split(':')[1]

            try:
                image_bytes = base64.b64decode(base64_data)
                img = Image.open(BytesIO(image_bytes)).convert("RGBA")
                width, height = img.size
                pixels = img.load()

                if mode == 1:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (0, 0, 0, 255 - avg([r,g,b]))
                elif mode == 2:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (255, 255, 255, 255 - avg([r,g,b]))
                elif mode == 3:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (r, g, b, 255 - avg([r,g,b]))
                elif mode == 4:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (r, g, b, 0)
                                else :
                                    pixels[x, y] = (0, 0, 0, 255)
                elif mode == 5:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (r, g, b, 0)
                                else :
                                    pixels[x, y] = (255, 255, 255, 255)
                elif mode == 6:
                        for x in range(width):
                            for y in range(height):
                                r, g, b, a = pixels[x, y]
                                if all(v >= 255-threshold for v in (r,g,b)):
                                    pixels[x, y] = (0, 0, 0, 0)

                output = BytesIO()
                img.save(output,"png")
                processed_data = output.getvalue()

                processed_base64 = base64.b64encode(processed_data).decode('ascii')
                new_href = f"data:{image_format};base64,{processed_base64}"
                image_element.set('xlink:href', new_href)

            except Exception as e:
                inkex.errormsg(f"Error processing image with id '{image_id}': {e}")

if __name__ == '__main__':
    KTX_White2Alpha().run()

