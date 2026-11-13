import os
import pandas as pd

class JeuDonnees:
    def __init__(self, fichier):
        donnees_brutes = charger_donnees(fichier)
        self.donnees = nettoyer_donnees(donnees_brutes)
        self.x, self.y = separer_donnees(self.donnees)
    
    def __len__(self):
        return len(self.donnees)


COLONNES_NUMERIQUES = ["HP", "Attack", "Defense", "Sp. Atk","Sp. Def", "Speed", "Generation"]
COLONNES_CATEGORIELLES = ["Type 1", "Type 2"]
COLONNES_CARACTERISTIQUES = (COLONNES_NUMERIQUES + COLONNES_CATEGORIELLES)

def charger_donnees(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        donnees = pd.read_csv(f)
        return donnees

def nettoyer_donnees(donnees):
    donnees = donnees.copy()
    
    for colonne in COLONNES_CATEGORIELLES:
        donnees[colonne] = donnees[colonne].fillna("Aucun")
        donnees[colonne] = donnees[colonne].replace("", "Aucun")
        donnees[colonne] = donnees[colonne].astype(str).str.strip()
    
    for colonne in COLONNES_NUMERIQUES:
        donnees[colonne] = pd.to_numeric(donnees[colonne], errors='raise')
    
    cible = donnees["Legendary"].astype("string").str.lower().str.strip()
    donnees["Legendary"] = cible.map({"true": True, "false": False})
    
    donnees = donnees.drop_duplicates()
    
    return donnees

def separer_donnees(donnees):
    x = donnees[COLONNES_CARACTERISTIQUES].copy()
    y = donnees["Legendary"].copy()
    return x, y