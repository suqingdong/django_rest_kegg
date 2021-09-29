from django.apps.config import MODELS_MODULE_NAME
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from django_rest_kegg.models import KEGG_PATHWAY_MODEL
import os
import requests


KEGG_DB_PATH = getattr(settings, 'KEGG_DB_PATH') or './keggdb'
KEGG_REST_URL = getattr(settings, 'KEGG_REST_URL') or 'http://rest.kegg.jp'



def get_pathway_list():
    resp = requests.get(f'{KEGG_REST_URL}/list/pathway')
    for line in resp.text.strip().split('\n'):
        map_number, desc = line.split('\t')
        map_number = map_number.split(':')[-1]
        yield (map_number, desc)


def download_file(url, outfile):
    resp = requests.get(url, stream=True)
    with open(outfile, 'wb') as out:
        for chunk in resp.iter_content(chunk_size=4096):
            out.write(chunk)


class Command(BaseCommand):
    """download kegg pathway data and build database
    """
    def add_arguments(self, parser):
        parser.add_argument('--drop', action='store_true', help='drop data before create.')

    def handle(self, *args, **options):
        if options.get('drop'):
            print('drop data from table')
            KEGG_PATHWAY_MODEL.objects.all().delete()


        print('start build kegg ...')
        for map_number, desc in get_pathway_list():
            map_image = f'{KEGG_DB_PATH}/pathway/{map_number}.png'
            map_conf = f'{KEGG_DB_PATH}/pathway/{map_number}.conf'
            if os.path.isfile(map_image) and os.path.isfile(map_conf):
                print(f'use local image and config for: {map_number}')
            else:
                print(f'downloading image and config for: {map_number}')
            
            m = KEGG_PATHWAY_MODEL(number=map_number, desc=desc, image=map_image, conf=map_conf)
            m.save()

            print(KEGG_PATHWAY_MODEL.objects.count())
