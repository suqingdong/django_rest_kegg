from django.urls import path, re_path
from django.conf.urls import url



from django_rest_kegg import views

urlpatterns = [
    path(r'pathway', views.KEGG_PATHWAY.as_view(), name='kegg-pathway'),
    # path(r'pathway/<str:map_number>', views.KEGG_PATHWAY.as_view(), name='list-pathway'),
]