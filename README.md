# 2026A-PRO2

## Description

Ce programme permet à l’utilisateur de saisir les caractéristiques d’un Pokémon, telles que ses types, ses points de vie (HP), sa génération, etc., puis de prédire si celui-ci est légendaire. Il a été réalisé dans le cadre du projet 2 du cours INF1007, à la session A2026, à Polytechnique Montréal.

## Table des matières

- [Description](#description)
- [Table des matières](#table-des-matières)
- [Installer et lancer l’application](#installer-et-lancer-lapplication)
- [Données](#données)
- [Modèle](#modèle)
- [Tests et couverture](#tests-et-couverture)
- [Structure du répertoire](#structure-du-répertoire)
- [Bibliothèques utilisées](#bibliothèques-utilisées)
- [Documentation consultée](#documentation-consultée)
- [Licence](#licence)
- [Auteurs](#auteurs)

## Installer et lancer l’application

Clonez d’abord le dépôt GitHub, puis accédez à la racine du projet dans votre terminal :

```shell
git clone https://github.com/RealMysticalAce/2026A-PRO2.git
cd 2026A-PRO2
```

Installez ensuite les dépendances indiquées dans le fichier `requirements.txt`, puis lancez le programme :

```shell
python -m pip install -r requirements.txt
python -m src.main
```

Vous pouvez maintenant remplir les champs de caractéristiques du Pokémon et cliquer sur Prédire. Le programme affiche le résultat sous le formulaire, présente un graphique des probabilités estimées que le Pokémon appartienne à chacune des deux catégories et ajoute la prédiction à l’historique. Vous pouvez consulter celui-ci dans l’onglet Historique des prédictions ou dans le fichier `modeles/historique.csv`.

## Données

Le jeu de données [« Pokémon with stats », d’Alberto Barradas](https://www.kaggle.com/datasets/abcsds/pokemon/data), a été trouvé sur Kaggle. Il contient 800 lignes et 13 colonnes. La cible est la colonne `Legendary`, qui indique si un Pokémon est légendaire (`True`) ou non (`False`).

Les neuf caractéristiques utilisées sont `Type 1`, `Type 2`, `HP`, `Attack`, `Defense`, `Sp. Atk`, `Sp. Def`, `Speed` et `Generation`. Le nom et le numéro ont été écartés, car ils servent à identifier le Pokémon. La colonne `Total` a également été exclue, puisqu’elle correspond à la somme des six statistiques de base.

La licence indiquée pour ce jeu de données est [CC0 : domaine public](https://creativecommons.org/publicdomain/zero/1.0/).

## Modèle

Le programme effectue une classification binaire pour prédire la valeur de `Legendary`. Le modèle utilisé est une régression logistique. Avant l’entraînement, les données numériques sont imputées par la médiane puis standardisées; les variables catégorielles sont encodées en variables indicatrices (one-hot encoding). Le modèle est entraîné avec une pondération équilibrée des classes.

Les données sont séparées en ensembles d’entraînement et de test selon un rapport de 80/20, avec une graine fixe et une stratification par classe. Le modèle est évalué avec le score F1 de la classe positive (`Legendary=True`) et comparé à une référence qui prédit toujours la classe majoritaire (`Legendary=False`). L'évaluation des modèles nous donne un score F1 de 0,727 pour le modèle et de 0,000 pour la référence. Ces résultats sont ceux enregistrés dans `modeles/metadonnees.json`.

## Tests et couverture

Les 18 tests du modèle et des données vérifient plusieurs aspects du fonctionnement du programme, notamment le nettoyage, le rejet des données invalides et la prédiction après le rechargement du modèle. Les mesures de couverture obtenues sont de 69 % pour `donnees.py` et de 91 % pour `modele.py`, soit 80 % au total selon le rapport utilisé.

Pour lancer les tests et produire le rapport de couverture :

```shell
coverage run --source=src -m pytest
coverage report --include="src/donnees.py,src/modele.py" -m
```

## Structure du répertoire

Voici la structure du répertoire du projet :

```text
.
├── donnees/
│   └── Pokemon.csv
├── modeles/
│   ├── graphique_exploration.png
│   ├── historique.csv
│   ├── metadonnees.json
│   └── modele.joblib
├── src/
│   ├── __init__.py
│   ├── donnees.py
│   ├── exceptions.py
│   ├── interface.py
│   ├── main.py
│   └── modele.py
├── tests/
│   ├── test_donnees.py
│   └── test_modele.py
├── .github/workflows/test.yml
├── .gitignore
├── DECISIONS.md
├── JOURNAL_IA.md
├── LICENSE
├── pytest.ini
└── requirements.txt
```

## Bibliothèques utilisées

Les bibliothèques utilisées par le programme sont indiquées dans le fichier `requirements.txt`. Pytest et Coverage servent à tester le programme et à mesurer la couverture du code. Pandas est utilisé pour charger et nettoyer les données. NumPy sert au calcul du score F1, et Matplotlib à la création des graphiques. Scikit-learn est utilisé pour entraîner et évaluer le modèle; joblib sert à le sauvegarder et à le recharger. Enfin, l’interface graphique a été conçue avec PyQt6.

## Documentation consultée

Les documentations officielles des bibliothèques et les notes de cours d’INF1007 ont servi à réaliser ce projet :

- [Documentation de NumPy](https://numpy.org/doc/)
- [Documentation de Matplotlib](https://matplotlib.org/stable/)
- [Documentation de scikit-learn](https://scikit-learn.org/stable/)
- [Documentation de PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Notes de cours d’INF1007](https://moodle.polymtl.ca/enrol/index.php?id=5293)

## Licence

Le code logiciel de ce projet est distribué sous licence MIT, comme indiqué dans le fichier `LICENSE`. La licence du jeu de données est la licence CC0 comme indiquée sur sa fiche Kaggle.

## Auteurs

- Valeriy Yauseichyk (2535614), groupe 04
- Anas Chraibi (2532521), groupe 04
