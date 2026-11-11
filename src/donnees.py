import pandas as pd

def charger_donnees(fichier):
    with open(fichier, 'r') as f:
        donnees = pd.read_csv(fichier)
        return donnees