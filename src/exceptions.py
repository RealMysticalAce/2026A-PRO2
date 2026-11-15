class FichierIntrouvableError(FileNotFoundError):
    """Le fichier CSV ou le modèle n'existe pas ou est introuvable."""

class DonneeInvalideError(ValueError):
    """Une donnée du CSV ou une saisie ne respecte pas le format attendu."""

class ColonneManquanteError(KeyError):
    """Une colonne requise est absente du CSV ou des caractéristiques."""

class SaisieHorsIntervalleError(DonneeInvalideError):
    """Une valeur numérique est hors de l'intervalle permis."""

class ModeleIndisponibleError(RuntimeError):
    """Le modèle est absent, illisible, incomplet ou pas encore entraîné."""

class SauvegardeModeleError(OSError):
    """Le modèle ou ses métadonnées n'ont pas pu être sauvegardés."""

class HistoriqueErreur(Exception):
    """L'historique des prédictions est illisible ou impossible à écrire."""