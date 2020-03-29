# Covid-19
Analyse des données sur le Covid-19 fournies par Santé Publique France

![logo](app/static/img/logo.png)



## Les données

- ### Données hospitalières relatives à l'épidémie de COVID-19

Récupérées sur le site des données publiques françaises et provenant de Santé Publique France, mises à jour quotidiennement.

Lien : https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/


- ### Données des urgences hospitalières et de SOS médecins relatives à l'épidémie de COVID-19

Récupérées sur le site des données publiques françaises et provenant de Santé Publique France, mises à jour quotidiennement.

Lien : https://www.data.gouv.fr/fr/datasets/donnees-des-urgences-hospitalieres-et-de-sos-medecins-relatives-a-lepidemie-de-covid-19/


- ### Données liées au recencement de la population française

Récupérées sur le site de l'INSEE. Données parues le 30/12/2019 et correspondantes à la population française en 2017, réparties par département.

Lien : https://www.insee.fr/fr/statistiques/4265429?sommaire=4265511


- ### Données du découpage des communes française

Récupérées sur le site de l'INSEE. Données parues le 26/02/2020 et correspondantes au code officiel géographique au premier janvier 2020.

Lien : https://www.insee.fr/fr/information/4316069



## Explications

Le fichier `data_visualisation.ipynb` comporte, entre autres, les fonctions :
- *afficheDepartement*, qui donne des informations propres à un département.
- *departementVsTous*, qui positionne un département par rapport aux autres.
- *afficheRegion*, qui donne des informations propres à une région.
- *regionVsTous*, qui positionne une région par rapport aux autres.
- *affichePays*, qui donne des informations propres au pays.



## Exemple

```python
idDep = 75
afficheDepartement(idDep)
departementVsTous(idDep)
```
![afficheDepartement](app/static/res/afficheDepartement-75.png)
![departementVsTous](app/static/res/departementVsTous-75.png)


```python
idReg = 11
afficheRegion(idReg)
regionVsTous(idReg)
```
![afficheRegion](app/static/res/afficheRegion-11.png)
![regionVsTous](app/static/res/regionVsTous-11.png)


```python
affichePays()
```
![affichePays](app/static/res/affichePays.png)



## Serveur de développement Flask

Ces fonction sont intégrées dans un serveur dans le dossier `app`.



## Modules Python utilisés

os, datetime, Pandas, seaborn, matplotlib

Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF, WTForms, Werkzeug 
