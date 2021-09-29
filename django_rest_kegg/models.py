from django.db import models


# Create your models here.
class KEGG_PATHWAY_MODEL(models.Model):
    number = models.CharField(max_length=15, verbose_name='map number', primary_key=True)
    desc = models.CharField(max_length=255, verbose_name='map description')
    image = models.ImageField(verbose_name='map image file')
    conf = models.FileField(verbose_name='map config file')
