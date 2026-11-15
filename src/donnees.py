import os

import pandas as pd

from .exceptions import FichierIntrouvableError, DonneeInvalideError

COLONNES_CATEGORIELLES = ["Type 1", "Type 2"]
COLONNES_NUMERIQUES = ["HP", "Attack", "Defense", "Sp. Atk","Sp. Def", "Speed", "Generation"]
COLONNES_CARACTERISTIQUES = (COLONNES_CATEGORIELLES + COLONNES_NUMERIQUES)
COLONNES_REQUISES = COLONNES_CARACTERISTIQUES + ["Legendary"]

class JeuDonnees:
    """Charge, nettoie et sépare les données du projet."""
    def __init__(self, fichier: str) -> None:
        """Charge le CSV et prépare ses caractéristiques et sa cible."""
        donnees_brutes = charger_donnees(fichier)
        self.donnees = nettoyer_donnees(donnees_brutes)
        self.x, self.y = separer_donnees(self.donnees)
    
    def __len__(self) -> int:
        """Retourne le nombre de lignes du jeu de données."""
        return len(self.donnees)

def charger_donnees(fichier: str) -> pd.DataFrame:
    """Charge le CSV ou lève une erreur s'il est absent ou illisible."""
    if not os.path.isfile(fichier):
        raise FichierIntrouvableError(f"Fichier CSV introuvable : {fichier}")
    
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            donnees = pd.read_csv(f)
    except FileNotFoundError:
        raise FichierIntrouvableError(f"Fichier CSV introuvable : {fichier}") 
    except pd.errors.ParserError:
        raise DonneeInvalideError("Le fichier CSV est mal formé ou contient des données invalides.")
    except pd.errors.EmptyDataError:
        raise DonneeInvalideError("Le fichier CSV est vide.")
    except pd.errors.ParserError:
        raise DonneeInvalideError("Le fichier CSV est mal formé.")
    except UnicodeDecodeError:
        raise DonneeInvalideError("Le fichier CSV n'utilise pas un encodage lisible.")
    except OSError as e:
        raise DonneeInvalideError(f"Impossible de lire le fichier CSV : {e}")
    
    if donnees.empty:
        raise DonneeInvalideError("Le fichier CSV ne contient aucune ligne de données.")
    
    return donnees

def nettoyer_donnees(donnees: pd.DataFrame) -> pd.DataFrame:
    """Nettoie les colonnes requises et retourne une copie."""
    if donnees.empty:
        raise DonneeInvalideError("Le jeu de données est vide.")
    
    donnees = donnees.copy()
    
    colonnes_manquantes = [colonne for colonne in COLONNES_REQUISES if colonne not in donnees.columns]
    if colonnes_manquantes:
        raise DonneeInvalideError(f"Colonnes requises manquantes : {colonnes_manquantes}")

    for colonne in COLONNES_CATEGORIELLES:
        try:
            donnees[colonne] = donnees[colonne].fillna("Aucun")
            donnees[colonne] = donnees[colonne].replace("", "Aucun")
            donnees[colonne] = donnees[colonne].astype(str).str.strip()
        except ValueError:
            raise DonneeInvalideError(f"Valeur inatendue dans la colonne catégorielle : {colonne}")
    
    for colonne in COLONNES_NUMERIQUES:
        try:
            donnees[colonne] = pd.to_numeric(donnees[colonne], errors='raise')
        except ValueError:
            raise DonneeInvalideError(f"Valeur inatendue dans la colonne numérique : {colonne}")
        except TypeError:
            raise DonneeInvalideError(f"Type de données incorrect dans la colonne numérique : {colonne}")
    
    try:
        cible = donnees["Legendary"].astype("string").str.lower().str.strip()
        donnees["Legendary"] = cible.map({"true": True, "false": False})
        if donnees["Legendary"].isna().any():
            raise DonneeInvalideError("Legendary doit contenir uniquement True ou False.")
    except KeyError:
        raise DonneeInvalideError("La colonne 'Legendary' est absente du jeu de données.")
    except ValueError:
        raise DonneeInvalideError("La colonne 'Legendary' contient des valeurs non booléennes.")
    
    donnees = donnees.drop_duplicates()
    
    return donnees

def separer_donnees(donnees: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Sépare les caractéristiques et la cible du jeu de données."""
    if donnees.empty:
        raise DonneeInvalideError("Le jeu de données est vide.")
    
    x = donnees[COLONNES_CARACTERISTIQUES].copy()
    y = donnees["Legendary"].copy()
    return x, y