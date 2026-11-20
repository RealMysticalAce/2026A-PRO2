import json

import joblib
import pandas as pd
import pytest

from src.donnees import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES
from src.exceptions import DonneeInvalideError, ModeleIndisponibleError
from src.modele import Modele


def donnees_pour_modele():
    """Crée 40 exemples équilibrés pour tester l'entraînement."""
    lignes = []
    cibles = []

    for index in range(40):
        legendaire = index % 2 == 1

        lignes.append({
            "Type 1": "Psychic" if legendaire else "Normal",
            "Type 2": "Aucun",
            "HP": 100 if legendaire else 40,
            "Attack": 120 if legendaire else 50,
            "Defense": 100 if legendaire else 50,
            "Sp. Atk": 120 if legendaire else 50,
            "Sp. Def": 100 if legendaire else 50,
            "Speed": 110 if legendaire else 50,
            "Generation": 3 if legendaire else 1,
        })
        cibles.append(legendaire)

    colonnes = COLONNES_CATEGORIELLES + COLONNES_NUMERIQUES
    x = pd.DataFrame(lignes, columns=colonnes)
    y = pd.Series(cibles, dtype=bool)

    return x, y


def test_constructeur_refuse_des_donnees_vides():
    colonnes = COLONNES_CATEGORIELLES + COLONNES_NUMERIQUES
    x = pd.DataFrame(columns=colonnes)
    y = pd.Series(dtype=bool)

    with pytest.raises(DonneeInvalideError):
        Modele(x, y)


def test_constructeur_refuse_des_longueurs_differentes():
    x, y = donnees_pour_modele()

    with pytest.raises(DonneeInvalideError):
        Modele(x, y.iloc[:-1])


def test_evaluer_refuse_un_modele_non_entraine():
    x, y = donnees_pour_modele()
    modele = Modele(x, y)

    with pytest.raises(ModeleIndisponibleError):
        modele.evaluer()


def test_predire_refuse_un_modele_non_entraine():
    x, y = donnees_pour_modele()
    modele = Modele(x, y)

    with pytest.raises(ModeleIndisponibleError):
        modele.predire(x.iloc[[0]])


def test_sauvegarder_refuse_un_modele_non_entraine():
    x, y = donnees_pour_modele()
    modele = Modele(x, y)

    with pytest.raises(ModeleIndisponibleError):
        modele.sauvegarder()


def test_entrainer_evaluer_predire_et_sauvegarder(tmp_path):
    x, y = donnees_pour_modele()
    modele = Modele(x, y)

    modele.entrainer()
    score = modele.evaluer()

    assert 0.0 <= score <= 1.0
    assert modele.f1_reference is not None

    prediction = modele.predire(x.iloc[[0]])
    assert isinstance(prediction, bool)

    probabilites = modele.modele.predict_proba(x.iloc[[0]])[0]
    assert sum(probabilites) == pytest.approx(1.0)

    dossier = tmp_path / "modeles"
    modele.sauvegarder(str(dossier))

    chemin_modele = dossier / "modele.joblib"
    chemin_metadonnees = dossier / "metadonnees.json"

    assert chemin_modele.is_file()
    assert chemin_metadonnees.is_file()

    pipeline_charge = joblib.load(chemin_modele)
    prediction_chargee = pipeline_charge.predict(x.iloc[[0]])[0]
    assert bool(prediction_chargee) == prediction

    with open(chemin_metadonnees, encoding="utf-8") as fichier:
        metadonnees = json.load(fichier)

    assert metadonnees["cible"] == "Legendary"
    assert "f1_modele" in metadonnees


def test_predire_refuse_des_caracteristiques_vides():
    x, y = donnees_pour_modele()
    modele = Modele(x, y)
    modele.entrainer()

    with pytest.raises(DonneeInvalideError):
        modele.predire(x.iloc[0:0])


def test_predire_refuse_une_colonne_manquante():
    x, y = donnees_pour_modele()
    modele = Modele(x, y)
    modele.entrainer()

    incompletes = x.iloc[[0]].drop(columns=["HP"])

    with pytest.raises(DonneeInvalideError):
        modele.predire(incompletes)