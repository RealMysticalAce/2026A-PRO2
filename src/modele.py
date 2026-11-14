import json
import os

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from .donnees import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES

class Modele:
    def __init__(self, x, y):
            self.x = x.copy() # categories
            self.y = y.copy() # cible
                        
            self.x_test = None
            self.x_train = None
            self.y_test = None
            self.y_train = None
    
            self.modele = None
            
            self.f1_modele = None
            self.f1_reference = None

    def entrainer(self):
        # separation donnees
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.x, self.y, test_size=0.2, random_state=0, stratify=self.y)
        
        # instructions de preparation
        preparation = ColumnTransformer([
            ("numeriques", SimpleImputer(strategy="median"), COLONNES_NUMERIQUES),
            ("categories", OneHotEncoder(handle_unknown="ignore"), COLONNES_CATEGORIELLES)])
        
        # instructions d'entrainement et entrainement du modele
        self.modele = Pipeline([("preparation", preparation), ("arbre", DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=0))])
        self.modele.fit(self.x_train, self.y_train)

    def evaluer(self):
        if self.modele is None:
            raise RuntimeError("Entraîne le modèle avant de l'évaluer.")

        predictions = self.modele.predict(self.x_test)
        self.f1_modele = f1_score(self.y_test, predictions, pos_label=True, zero_division=0)

        reference = DummyClassifier(strategy="most_frequent")
        reference.fit(self.x_train, self.y_train)
        
        predictions_reference = reference.predict(self.x_test)
        self.f1_reference = f1_score(self.y_test, predictions_reference, pos_label=True, zero_division=0)

        print(f"F1 référence : {self.f1_reference:.3f}")
        print(f"F1 du modèle : {self.f1_modele:.3f}")
        print(classification_report(self.y_test, predictions, labels=[False, True], target_names=["Non légendaire", "Légendaire"], zero_division=0))

        return self.f1_modele

    def sauvegarder(self, dossier = "modeles"):
        if self.modele is None or self.f1_modele is None:
            raise RuntimeError("Entraîne et évalue le modèle avant de le sauvegarder.")

        os.makedirs(dossier, exist_ok=True)

        chemin_modele = os.path.join(dossier, "modele_arbre_decisions.joblib")
        joblib.dump(self.modele, chemin_modele)

        metadonnees = {
            "cible": "Legendary",
            "colonnes_numeriques": COLONNES_NUMERIQUES,
            "colonnes_categorielles": COLONNES_CATEGORIELLES,
            "valeurs_categorielles": {
                colonne: sorted(self.x[colonne].dropna().astype(str).unique().tolist())
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

    def predire(self, caracteristiques):
        if self.modele is None:
            raise RuntimeError("Il faut entraîner le modèle avant de prédire.")

        prediction = self.modele.predict(caracteristiques)
        return bool(prediction[0])