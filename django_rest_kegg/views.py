import io
import base64

import PIL
from PIL import ImageDraw, ImageColor

from pysvg.structure import Svg, Image
from pysvg.shape import Rect, Circle
from pysvg.linking import A
# from pysvg.style import Style
# from pysvg.text import Text

from django.conf import settings
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from django_rest_kegg.models import KEGG_PATHWAY_MODEL
from django_rest_kegg import utils


KEGG_BASE_URL = settings.KEGG_BASE_URL if hasattr(
    settings, 'KEGG_BASE_URL') else 'http://www.kegg.jp'

KEGG_KEEP_SHAPES = settings.KEGG_KEEP_SHAPES if hasattr(
    settings, 'KEGG_KEEP_SHAPES') else None


class KEGG_PATHWAY_VIEW(APIView):
    name = 'KEGG Pathway List'

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
            :params path: path number
            :params gene: genelist to highlight
            :params type: return type, default png
        """
        map_number = request.query_params.get('path')
        gene = request.query_params.get('gene')
        ret_type = request.query_params.get('type')
        default_color = request.query_params.get('color', 'green')

        print(request.query_params)

        if map_number:
            res = KEGG_PATHWAY_MODEL.objects.filter(number=map_number).first()
            if not res:
                data = {'error': f'map number not exists: {map_number}'}
                return Response(data, status=404)
            if ret_type == 'conf':
                return FileResponse(res.conf.open(),
                                    content_type='text/plain',
                                    as_attachment=False,
                                    filename=res.number + '.conf.txt')
            return self.response_wrapper(res, gene, ret_type, default_color)

        all_pathways = KEGG_PATHWAY_MODEL.objects.all()
        data = {each.number: each.desc for each in all_pathways}
        return Response({'total': all_pathways.count(), 'pathways': data})

    def response_wrapper(self, obj, gene, ret_type, default_color):
        """
        """
        ret_type = ret_type or 'png'
        filename = f'{obj.number}.{ret_type}'
        if gene:
            gene_color = utils.parse_gene(gene, default_color)
            if not gene_color:
                return Response({'error': 'bad gene format'}, status=501)
            conf_data = list(utils.parse_conf(
                obj.conf, keep_shapes=KEGG_KEEP_SHAPES))

            file = self.build_png(obj.image, conf_data, gene_color)

            if ret_type == 'svg':
                file = self.build_svg(file, conf_data)
        else:
            file = obj.image.open('rb')

        return FileResponse(file, filename=filename)

    def build_png(self, img, conf_data, gene_color):
        im = PIL.Image.open(img)
        draw = ImageDraw.Draw(im)
        for shape, position, _, title in conf_data:
            color = utils.get_gene_color(title, gene_color)
            if not color:
                continue

            try:
                color_rgba = ImageColor.getcolor(color, 'RGBA')
            except:
                color_rgba = ImageColor.getcolor(f'#{color}', 'RGBA')

            if not color_rgba:
                continue

            if shape == 'rect':
                X, Y, RX, RY = position
                for x in range(X, RX):
                    for y in range(Y, RY):
                        # pixel > 0 means this point is not black
                        if im.getpixel((x, y))[0] > 0:
                            ImageDraw.floodfill(
                                im, xy=(x, y), value=color_rgba)
            else:
                CX, CY, R = position
                X, Y, RX, RY = CX - R, CY - R, CX + R, CY + R
                draw.ellipse([(X, Y), (RX, RY)], fill=color_rgba)

        file = io.BytesIO()
        im.save(file, format='png')
        file.seek(0)
        return file

    def build_svg(self, file, conf_data):
        # build a svg object, which size is the same as background
        width, height = PIL.Image.open(file).size

        svg = Svg(width=width, height=height)
        file.seek(0)
        png_link = 'data:image/png;base64,' + \
            base64.b64encode(file.read()).decode()

        im = Image(x=0, y=0, width=width, height=height)
        im.set_xlink_href(png_link)
        svg.addElement(im)

        for shape, position, url, title in conf_data:
            a = A(target='new_window')
            a.set_xlink_title(title)
            a.set_xlink_href(KEGG_BASE_URL + url)
            svg.addElement(a)

            child = self.add_child(shape, position)
            if child:
                a.addElement(child)
            svg.addElement(a)

        file = io.BytesIO()
        file.write(svg.getXML().encode())
        file.seek(0)

        return file

    @staticmethod
    def add_child(shape, position):
        if shape == 'rect':
            x, y, rx, ry = position
            w, h = rx - x, ry - y
            child = Rect(x=x, y=y, width=w, height=h)
        elif shape == 'circ':
            cx, cy, r = position
            child = Circle(cx=cx, cy=cy, r=r)
        else:
            return

        style = 'fill-opacity: 0'
        child.set_style(style)
        return child
