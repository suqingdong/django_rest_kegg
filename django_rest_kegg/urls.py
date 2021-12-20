from django.urls import path
from django_rest_kegg.views import KEGG_PATHWAY_VIEW


urlpatterns = [
    path(r'pathway', KEGG_PATHWAY_VIEW.as_view(), name='kegg-pathway'),
]
