import json
import os
import pandas as pd
import numpy as np

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression

from .exceptions import (DonneeInvalideError, ModeleIndisponibleError, SauvegardeModeleError)

from .donnees import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES

class Modele:
    """Entraîne, évalue, sauvegarde et utilise le modèle de régression logistique."""
    def __init__(self, x: pd.DataFrame, y: pd.Series) -> None:
        """Vérifie les entrées et les conserve dans l'objet."""
        if x.empty or y.empty:
            raise DonneeInvalideError("Les caractéristiques ou la cible sont vides.")
        if len(x) != len(y):
            raise DonneeInvalideError("X et Y doivent avoir le même nombre de lignes.")
        
        self.x = x.copy() # categories
        self.y = y.copy() # cible
        
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None

        self.modele = None            
        self.f1_modele = None
        self.f1_reference = None

    def entrainer(self) -> None:
        """Sépare les données et entraîne le modèle."""        
        # separation donnees
        try:
            self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=0.2, random_state=0, stratify=self.y)
        except ValueError as e:
            raise DonneeInvalideError(f"Erreur lors de la séparation des données : {e}")

        # instructions de preparation
        preparation_numerique = Pipeline([("imputation", SimpleImputer(strategy="median")), ("standardisation", StandardScaler())])
        preparation = ColumnTransformer([("numeriques", preparation_numerique, COLONNES_NUMERIQUES), ("categories", OneHotEncoder(handle_unknown="ignore"), COLONNES_CATEGORIELLES)])

        self.modele = Pipeline([("preparation", preparation), ("classifieur", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=0))])  
        self.modele.fit(self.x_train, self.y_train)
        
        print("Modèle entraîné avec succès.")
        print(f"Valeurs du modèle : {self.modele.named_steps['classifieur'].classes_}")

    @staticmethod
    def calculer_f1(y_reel: pd.Series, y_predit: np.ndarray) -> float:
        """Retourne le F1 de la classe True à partir de booléens.

        Lève DonneeInvalideError si les vecteurs sont vides, de dimensions
        incorrectes ou de longueurs différentes.
        """
        reels = np.asarray(y_reel, dtype=bool)
        predits = np.asarray(y_predit, dtype=bool)

        if reels.ndim != 1 or reels.shape != predits.shape or reels.size == 0:
            raise DonneeInvalideError(
                "Deux vecteurs non vides de même longueur sont requis."
            )

        vrais_positifs = np.sum(reels & predits)
        faux_positifs = np.sum(~reels & predits)
        faux_negatifs = np.sum(reels & ~predits)

        denominateur = 2 * vrais_positifs + faux_positifs + faux_negatifs

        if denominateur == 0:
            return 0.0

        return float(2 * vrais_positifs / denominateur)


    def evaluer(self) -> float:
        """Évalue le modèle et calcule le F1 score."""
        if self.modele is None:
            raise ModeleIndisponibleError("Le modèle n'est pas encore entraîné.")
        if self.x_test is None or self.y_test is None:
            raise ModeleIndisponibleError("Le jeu de test n'est pas disponible.")
        try:
            predictions = self.modele.predict(self.x_test)
            self.f1_modele = f1_score(self.y_test, predictions, pos_label=True, zero_division=0)

            reference = DummyClassifier(strategy="most_frequent")
            reference.fit(self.x_train, self.y_train)
            
            predictions_reference = reference.predict(self.x_test)
            self.f1_reference = f1_score(self.y_test, predictions_reference, pos_label=True, zero_division=0)
        except ValueError as e:
            raise DonneeInvalideError(f"Erreur lors de l'évaluation du modèle : {e}")
        
        f1_numpy = self.calculer_f1(self.y_test, predictions)
        
        print("Évaluation du modèle :")
        print(f"F1 référence : {self.f1_reference:.3f}")
        print(f"F1 du modèle : {self.f1_modele:.3f}")
        print(f"F1 calculé par NumPY : {f1_numpy:.3f}")
        print(classification_report(self.y_test, predictions, labels=[False, True], target_names=["Non légendaire", "Légendaire"], zero_division=0))

        return self.f1_modele

    def sauvegarder(self, dossier: str = "modeles") -> None:
        """Sauvegarde le modèle entraîné et les métadonnées."""
        if self.modele is None or self.f1_modele is None:
            raise ModeleIndisponibleError("Veuillez entraîner et évaluer le modèle avant de le sauvegarder.")

        try:
            os.makedirs(dossier, exist_ok=True)

            chemin_modele = os.path.join(dossier, "modele.joblib")
            joblib.dump(self.modele, chemin_modele)

            metadonnees = {
                "cible": "Legendary",
                "colonnes_numeriques": COLONNES_NUMERIQUES,
                "colonnes_categorielles": COLONNES_CATEGORIELLES,
                "valeurs_categorielles": {
                    colonne: sorted(
                        self.x[colonne].dropna().astype(str).unique().tolist(),
                        key=lambda valeur: valeur.casefold(),
                    )
                    for colonne in COLONNES_CATEGORIELLES},
                "intervalles_numeriques": {
                    colonne: {"minimum": float(self.x[colonne].min()), "maximum": float(self.x[colonne].max())}
                    for colonne in COLONNES_NUMERIQUES},
                "f1_modele": self.f1_modele,
                "f1_reference": self.f1_reference
            }

            chemin_json = os.path.join(dossier, "metadonnees.json")
            with open(chemin_json, "w", encoding="utf-8") as fichier:
                json.dump(metadonnees, fichier, indent=4, ensure_ascii=False)
        except OSError as e:
            raise SauvegardeModeleError(f"Impossible de sauvegarder le modèle : {e}")

    def predire(self, caracteristiques: pd.DataFrame) -> bool:
        """Prédit le statut légendaire d'une ligne de caractéristiques."""
        if self.modele is None:
            raise ModeleIndisponibleError("Entraîne ou charge le modèle avant de prédire.")

        if caracteristiques.empty:
            raise DonneeInvalideError("Aucune caractéristique n'a été fournie.")

        try:
            prediction = self.modele.predict(caracteristiques)
        except (ValueError, TypeError):
            raise DonneeInvalideError("Les caractéristiques fournies ne peuvent pas être prédites.")

        return bool(prediction[0])