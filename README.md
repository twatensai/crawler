# Crawler

Un crawler éthique réalisé par Thibaut WOJDACKI

## Comment faire fonctionner le crawler ?

Première étape : Aller dans le bon dossier `cd crawler`

Deuxième étape  : Installer les packages nécessaires - `pip install -r requirements.txt`

Troisième étape : Lancer l'application  `python main.py`

## Paramètres à modifier

Avant la troisième étape, il est possible de modifier des paramètres afin d'ajuster le crawler à ses besoins !

Il faut modifier la partie : `crawler = Crawler("https://ensai.fr/", max_urls=10, max_links='all')`

Les paramètres du crawler sont :

- L'URL de départ du crawler identifiée par la variable `start_url`. Ce champ est obligatoire !
- Le nombre maximum d'URL que l'on veut crawler identifié par la variable `max_urls`. Ce champ est optionnel. Sa valeur par défaut est 50.
- Le nombre maximum de liens que l'on veut récupérer sur une page web identifié par la variable `max_links`. Ce champ est optionnel, il peut prendre des valeurs entières supérieures ou égales à zéro. Zéro signifiant qu'on ne veut récupérer aucun lien. Il est possible de mettre ce paramètre à 'all' pour récupérer tous les liens issues d'une page web. Sa valeur par défaut est 5.
- Si on souhaite récupérer les fichiers sitemap.xml à partir du fichier robots.txt, la variable `use_sitemap` permet de le faire. Ce champ est optionnel. Sa valeur par défaut est True, la mettre à False pour désactiver cette fonctionnalité.

## Fonctionnalité du crawler

Le crawler respecte le fichier robots.txt et sauvegarde dans un dictionnaire les fichiers robots.txt déjà parcouru lié à la base de l'URL. Si une base d'un URL est connu dans ce dictionnaire, le crawler vérifie juste qu'il a le droit de crawler avec le fichier robots.txt qu'il a en mémoire.
Le crawler respecte la politeness, celle-ci est fixé à 3 secondes entre chaque appel, auquel on soustrait la vitesse de téléchargement de la dernière page.
Le crawler peut lire le fichier sitemap si celui-ci est renseigné dans le fichier robots.txt, il parcourt toute l'arborescence du celui-ci.
Une base de données relationnelle (DataFrame Pandas) est créée et stocke l'URL des pages web trouvées ainsi que la date de crawling (age). (Il sera possible facilement de lier cela à une base Postgre ou autres. Pas implémenté)
Le crawler ne permet pas le multithreading. Il aurait fallu changer la gestion de la Queue, instaurer un timeout sur le get, j'ai essayé mais le code avait quelques soucis.
