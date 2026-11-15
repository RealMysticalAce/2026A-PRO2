import pandas as pd
import pytest

from src.donnees import (
    COLONNES_CARACTERISTIQUES,
    JeuDonnees,
    charger_donnees,
    nettoyer_donnees,
    separer_donnees,
)
from src.exceptions import DonneeInvalideError, FichierIntrouvableError


def tableau_valide():
    """Crée un petit tableau Pokémon utilisé par les tests."""
    return pd.DataFrame({
        "Type 1": ["Grass", "Fire"],
        "Type 2": [None, "Flying"],
        "HP": ["45", "39"],
        "Attack": ["49", "52"],
        "Defense": ["49", "43"],
        "Sp. Atk": ["65", "60"],
        "Sp. Def": ["65", "50"],
        "Speed": ["45", "65"],
        "Generation": ["1", "1"],
        "Legendary": ["False", " TRUE "],
    })


def test_charger_donnees_lit_un_csv(tmp_path):
    chemin = tmp_path / "pokemon.csv"
    tableau_valide().to_csv(chemin, index=False)

    donnees = charger_donnees(str(chemin))

    assert len(donnees) == 2
    assert "Legendary" in donnees.columns


def test_charger_donnees_refuse_un_fichier_absent():
    with pytest.raises(FichierIntrouvableError):
        charger_donnees("fichier_absent.csv")


def test_charger_donnees_refuse_un_fichier_vide(tmp_path):
    chemin = tmp_path / "vide.csv"
    chemin.write_text("", encoding="utf-8")

    with pytest.raises(DonneeInvalideError):
        charger_donnees(str(chemin))


def test_nettoyer_convertit_les_types_nombres_et_cible():
    nettoyees = nettoyer_donnees(tableau_valide())

    assert nettoyees["Type 2"].iloc[0] == "Aucun"
    assert nettoyees["HP"].tolist() == [45, 39]
    assert nettoyees["Legendary"].tolist() == [False, True]


def test_nettoyer_ne_modifie_pas_le_tableau_original():
    original = tableau_valide()
    copie_originale = original.copy(deep=True)

    nettoyer_donnees(original)

    pd.testing.assert_frame_equal(original, copie_originale)


def test_nettoyer_refuse_une_colonne_manquante():
    donnees = tableau_valide().drop(columns=["HP"])

    with pytest.raises(DonneeInvalideError):
        nettoyer_donnees(donnees)


def test_nettoyer_refuse_une_valeur_numerique_invalide():
    donnees = tableau_valide()
    donnees.loc[0, "Attack"] = "Cinquante"

    with pytest.raises(DonneeInvalideError):
        nettoyer_donnees(donnees)


def test_nettoyer_refuse_une_cible_inconnue():
    donnees = tableau_valide()
    donnees.loc[0, "Legendary"] = "Oui"

    with pytest.raises(DonneeInvalideError):
        nettoyer_donnees(donnees)


def test_separer_retourne_x_et_y():
    donnees = nettoyer_donnees(tableau_valide())

    x, y = separer_donnees(donnees)

    assert list(x.columns) == COLONNES_CARACTERISTIQUES
    assert y.tolist() == [False, True]
    assert len(x) == len(y)


def test_jeu_donnees_len_retourne_le_nombre_de_lignes(tmp_path):
    chemin = tmp_path / "pokemon.csv"
    tableau_valide().to_csv(chemin, index=False)

    jeu = JeuDonnees(str(chemin))

    assert len(jeu) == 2