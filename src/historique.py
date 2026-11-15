"""Lire et conserver localement les prédictions dans un fichier JSON."""

from datetime import datetime
import json
import os

from .exceptions import HistoriqueErreur


class Historique:
    """Stockage des prédictions à l'emplacement choisi par le lanceur."""

    def __init__(self, chemin: str) -> None:
        """Mémorise le chemin du fichier JSON sans l'ouvrir."""
        self._chemin = os.path.abspath(chemin)

    def lire(self) -> list[dict]:
        """Renvoie les prédictions ou une liste vide si le fichier est absent."""
        if not os.path.exists(self._chemin):
            return []

        try:
            with open(self._chemin, encoding="utf-8") as fichier:
                entrees = json.load(fichier)
        except (OSError, ValueError) as erreur:
            raise HistoriqueErreur("Impossible de lire l'historique JSON.") from erreur

        if not isinstance(entrees, list) or not all(self._valide(entree) for entree in entrees):
            raise HistoriqueErreur("Le fichier d'historique a un format invalide.")
        
        return entrees

    @staticmethod
    def _valide(entree: object) -> bool:
        """Indique si une entrée JSON contient les données attendues."""
        return (
            isinstance(entree, dict)
            and isinstance(entree.get("date"), str)
            and isinstance(entree.get("saisies"), dict)
            and isinstance(entree.get("legendaire"), bool)
            and isinstance(entree.get("probabilite_legendaire"), (int, float))
            and 0 <= entree["probabilite_legendaire"] <= 1
        )

    def ajouter(self, valeurs: dict, legendaire: bool, probabilite: float) -> dict:
        """Enregistre et retourne une prédiction; erreur d'écriture : HistoriqueErreur."""
        entree = {
            "date": datetime.now().isoformat(timespec="seconds"),
            "saisies": dict(valeurs),
            "legendaire": legendaire,
            "probabilite_legendaire": probabilite,
        }

        if not self._valide(entree):
            raise HistoriqueErreur("La prédiction ne peut pas être enregistrée : format invalide.")

        entrees = self.lire()
        entrees.append(entree)
        temporaire = self._chemin + ".tmp"

        try:
            os.makedirs(os.path.dirname(self._chemin), exist_ok=True)

            with open(temporaire, "w", encoding="utf-8") as fichier:
                json.dump(entrees, fichier, ensure_ascii=False, indent=2, allow_nan=False)

            os.replace(temporaire, self._chemin)
        except (OSError, ValueError, TypeError) as erreur:
            raise HistoriqueErreur("Impossible d'enregistrer la prédiction dans l'historique.") from erreur
        
        return entree