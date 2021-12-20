from pathlib import Path

import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from django_rest_kegg.models import KEGG_PATHWAY_MODEL


KEGG_DB_PATH = settings.KEGG_DB_PATH if hasattr(settings, 'KEGG_DB_PATH') else './keggdb'
KEGG_REST_URL = settings.KEGG_REST_URL if hasattr(settings, 'KEGG_REST_URL') else 'http://rest.kegg.jp'


def get_pathway_list():
    resp = requests.get(f'{KEGG_REST_URL}/list/pathway')
    for line in resp.text.strip().split('\n'):
        map_number, desc = line.split('\t')
        map_number = map_number.split(':')[-1]
        yield (map_number, desc)


def download_file(url, outfile):
    resp = requests.get(url, stream=True)

    outfile = Path(outfile)

    if not outfile.parent.exists():
        outfile.parent.mkdir(parents=True)

    with outfile.open('wb') as out:
        for chunk in resp.iter_content(chunk_size=4096):
            out.write(chunk)


class Command(BaseCommand):
    """download kegg pathway data and build database
    """
    def add_arguments(self, parser):
        parser.add_argument('--drop', action='store_true', help='drop data before create.')
        parser.add_argument('--dbpath', help='the path to store kegg pathway data[default: %(default)s]', default=KEGG_DB_PATH)

    def handle(self, *args, **options):
        if options.get('drop'):
            print('drop all data from table')
            KEGG_PATHWAY_MODEL.objects.all().delete()

        dbpath = Path(options.get('dbpath'))
        print(dbpath)

        print('start build kegg ...')
        for map_number, desc in get_pathway_list():
            map_image = dbpath.joinpath('pathway', f'{map_number}.png')
            map_conf = dbpath.joinpath('pathway', f'{map_number}.conf')
            if map_image.is_file() and map_conf.is_file():
                print(f'use local image and config for: {map_number}')
            else:
                print(f'downloading image and config for: {map_number}')
                download_file(f'{KEGG_REST_URL}/get/{map_number}/image', str(map_image))
                download_file(f'{KEGG_REST_URL}/get/{map_number}/conf', str(map_conf))
            
            m = KEGG_PATHWAY_MODEL(number=map_number, desc=desc, image=str(map_image), conf=str(map_conf))
            m.save()

            print(KEGG_PATHWAY_MODEL.objects.count())
