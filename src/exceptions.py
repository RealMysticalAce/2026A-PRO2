"""Exceptions du projet, traduites en messages lisibles par l'interface."""


class DonneeInvalideError(ValueError):
    """Une donnée du CSV ou une saisie ne respecte pas le format attendu."""


class ModeleIndisponibleError(RuntimeError):
    """Le modèle est absent, illisible, incomplet ou pas encore entraîné."""


class HistoriqueErreur(Exception):
    """L'historique des prédictions est illisible ou impossible à écrire."""