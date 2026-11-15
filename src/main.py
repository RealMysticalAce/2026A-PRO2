import json
import os

import matplotlib.pyplot as plt
import joblib as jb

from .donnees import JeuDonnees
from .modele import Modele
from .interface import lancer_interface

from .exceptions import FichierIntrouvableError, DonneeInvalideError

def main() -> int:
    """Charge les fichiers sauvegardés et lance l'interface."""
    chemin_modele = "modeles/modele.joblib"
    chemin_metadonnees = "modeles/metadonnees.json"
    chemin_historique = "modeles/historique.csv"
    try:
        if not os.path.isfile(chemin_modele):
            raise FichierIntrouvableError(f"Modèle introuvable : {chemin_modele}")
        if not os.path.isfile(chemin_metadonnees):
            raise FichierIntrouvableError(f"Métadonnées introuvables : {chemin_metadonnees}")
        modele = jb.load(chemin_modele)
        metadonnees = json.load(open(chemin_metadonnees, "r", encoding="utf-8"))
    except FichierIntrouvableError as e:
        print(f"Fichier requis absent : {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Le fichier de métadonnées JSON est invalide : {e}")
        return 1
    except DonneeInvalideError as e:
        print(f"Métadonnées invalides : {e}")
        return 1
    except (OSError, EOFError, ValueError, ImportError) as e:
        print(f"Impossible de charger le modèle ou ses métadonnées : {e}")
        return 1

    return lancer_interface(modele, metadonnees, chemin_historique)

def exploration() -> None:
    """Crée et enregistre le graphique exploratoire."""
    jeu = JeuDonnees("donnees/pokemon.csv").donnees
    plt.title("Nombre de Pokémon légendaires vs non légendaires")
    plt.xlabel("Légendaire")
    plt.ylabel("Nombre de Pokémon")
    plt.bar_label(plt.bar(["Non-légendaire", "Légendaire"], jeu["Legendary"].value_counts().values, color=["lightblue", "gold"]), labels=jeu["Legendary"].value_counts().values, padding=3)
    plt.ylim(0, jeu["Legendary"].value_counts().values.max() + 50)
    plt.savefig("modeles/graphique_exploration.png")
    plt.show()

def entrainement() -> None:
    """Entraîne, évalue et sauvegarde le modèle."""
    jeu = JeuDonnees("donnees/pokemon.csv")
    modele = Modele(jeu.x, jeu.y)
    modele.entrainer()
    modele.evaluer()
    modele.sauvegarder()

if __name__ == "__main__":
    # exploration()
    # entrainement()
    raise SystemExit(main())