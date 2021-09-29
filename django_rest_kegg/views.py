import re
import io
import json
import base64

import PIL
from PIL import ImageDraw, ImageColor

from pysvg.structure import Svg, Image
from pysvg.shape import Rect, Circle
from pysvg.style import Style
from pysvg.linking import A
from pysvg.text import Text


from django.http import FileResponse, HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions

from django_rest_kegg.models import KEGG_PATHWAY_MODEL


class KEGG_PATHWAY(APIView):
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
                return FileResponse(res.conf.open(), filename=res.number + '.conf.txt')
            return self.response_wrapper(res, gene, ret_type, default_color)

        all_pathways = KEGG_PATHWAY_MODEL.objects.all()
        data = {each.number: each.desc for each in all_pathways}
        return Response(data)

    def response_wrapper(self, obj, gene, ret_type, default_color):
        """
        """
        ret_type = ret_type or 'png'
        filename = f'{obj.number}.{ret_type}'
        if gene:
            gene_color = self.parse_gene(gene, default_color)
            if not gene_color:
                return Response({'error': 'bad gene format'}, status=501)
            conf_data = list(self.parse_conf(obj.conf))

            file = self.build_png(obj.image, conf_data, gene_color)

            if ret_type == 'svg':
                file = self.build_svg(file, conf_data)
        else:
            file = obj.image.open('rb')

        return FileResponse(file, filename=filename)

    def build_png(self, img, conf_data, gene_color):
        im = PIL.Image.open(img)
        for shape, position, _, title in conf_data:
            color = self.get_gene_color(title, gene_color)
            if not color or shape != 'rect':
                continue
            X, Y, RX, RY = position

            try:
                try:
                    color_rgba = ImageColor.getcolor(color, 'RGBA')
                except:
                    color_rgba = ImageColor.getcolor(f'#{color}', 'RGBA')
                print(color, color_rgba)
                for x in range(X, RX):
                    for y in range(Y, RY):
                        # pixel > 0 means this point is not black
                        if im.getpixel((x, y))[0] > 0:
                            ImageDraw.floodfill(im, xy=(x, y), value=color_rgba)
            except:
                print('this color is invalid: {}'.format(color))

        im.save('tmp.png')

        file = io.BytesIO()
        im.save(file, format='png')
        file.seek(0)
        return file

    def build_svg(self, file, conf_data):
        # build a svg object, which size is the same as background
        width, height = PIL.Image.open(file).size

        svg = Svg(width=width, height=height)
        file.seek(0)
        png_link = 'data:image/png;base64,' + base64.b64encode(file.read()).decode()

        print(file)
        print(png_link[:100])

        im = Image(x=0, y=0, width=width, height=height)
        im.set_xlink_href(png_link)
        svg.addElement(im)

        for shape, position, url, title in conf_data:
            a = A(target='new_window')
            a.set_xlink_title(title)
            a.set_xlink_href(url)
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


    @staticmethod
    def get_gene_color(title, gene_color, conflict_color='green'):
        color = None
        result = re.findall(r'([^\s]+) \((.+?)\)', title)
        if result:
            gene_in_title = [each for part in result for each in part]
            for gene in gene_in_title:
                if gene_color.get(gene):
                    # conflict color in a gene family
                    if color and color != gene_color[gene]:
                        color = conflict_color
                    else:
                        color = gene_color[gene]
        return color

    def parse_conf(self, conf, keep_shapes=('rect',)):
        with conf.open() as f:
            for line in f:
                linelist = line.decode().strip().split('\t')
                res = [each for each in re.split(
                    r'[\s,\(\)]', linelist[0]) if each]
                shape = res[0]
                position = list(map(int, res[1:]))

                url = linelist[1]
                title = linelist[2]

                if shape in keep_shapes:
                    yield shape, position, url, title

    def parse_gene(self, gene, default_color):
        """
        """
        try:
            # gene={"red": "K01,K02", "blue": "K03,K04,K05"}
            # gene=["K01,K02,K03"]&color=red
            color_genes = json.loads(gene)
            if isinstance(color_genes, list):
                gene_color_map = {
                    g: default_color for g in color_genes[0].split(',')}
            elif isinstance(color_genes, dict):
                gene_color_map = {}
                for color, genes in color_genes.items():
                    for gene in genes.split(','):
                        gene_color_map[gene] = color
            else:
                return False
            print('>>> gene colors:', gene_color_map)
            return gene_color_map
        except:
            return False
