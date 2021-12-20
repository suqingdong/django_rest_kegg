# Application of KEGG REST API with DRF(DjangoRestFramework)

## Installation
```bash
python3 -m pip install django_rest_kegg
```

## Install App to Your Djanog Rest Project
1 edit `proj/settings.py`
```python
INSTALL_APPS += [
    'rest_framework',
    'django_rest_kegg'
]

# the path to store image and conf files
KEGG_DB_PATH = './keggdb'
```
2 edit `proj/urls.py`
```python
urlpatterns += [
    path('kegg/', include('django_rest_kegg.urls')),
]
```

## Initialize KEGG Database
```bash
# migarate database
python3 manage.py makemigrations django_rest_kegg
python3 manage.py migrate

# download image and conf files for all pathways
# and build table
python3 manage.py build [--dbpath PATH] [--drop]

# everything is ok, enjoy it!
python3 manage.py runserver
```

## Endpoints
### `/kegg/pathway`  list all pathways

### `/kegg/pathway?path=<PATH>&type=<TYPE>&gene=<GENE>&color=<COLOR>`
- path: a map number, eg. map00010
- type: conf, svg or png [default: png]
- color: default color [default: green]
- gene: genes to be highlighted, example formats:
    - `gene={"red":"K00886,K01222,K01223"}`
    - `gene={"FF00FF":"K00886,K01222,K01223"}`
    - `gene={"red":"K00886,K01222","blue":"K01610,K00918"}`
    - `gene=["K00886,K01222,K01223"]`
    - `gene=["K00886,K01222,K01223"]&color=pink`

## Demo Project
```bash
git clone https://www.github.com/suqingdong/django_rest_kegg.git

cd django_rest_kegg/demo

python3 manage.py makemigrations django_rest_kegg

python3 manage.py migrate
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, django_rest_kegg, sessions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   Applying admin.0001_initial... OK
#   ...
#   Applying django_rest_kegg.0001_initial... OK
#   Applying sessions.0001_initial... OK

python3 manage.py build

python3 manage.py runserver
```
