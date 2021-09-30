import re
import json


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


def parse_conf(conf, keep_shapes=('rect',)):
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


def parse_gene(gene, default_color):
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
