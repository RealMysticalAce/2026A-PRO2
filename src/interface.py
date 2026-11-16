import csv
import os
import sys
from datetime import datetime
from .donnees import VariableNumerique, VariableCategorielle

import pandas as pd
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QMessageBox)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from .modele import Modele
from .donnees import COLONNES_CARACTERISTIQUES
from .exceptions import (DonneeInvalideError, HistoriqueErreur, ModeleIndisponibleError)


class Fenetre(QWidget):
    """Affiche les champs de saisie, la prédiction et son graphique."""

    def __init__(self, modele: Modele, metadonnees: dict, chemin_historique: str) -> None:
        """Crée l'interface graphique."""
        if modele is None or not callable(getattr(modele, "predict", None)):
            raise ModeleIndisponibleError("Le modèle est absent ou ne permet pas de faire des prédictions.")
        cles_requises = ["colonnes_categorielles", "colonnes_numeriques", "valeurs_categorielles", "intervalles_numeriques"]
        for cle in cles_requises:
            if cle not in metadonnees:
                raise DonneeInvalideError(f"Les métadonnées sont invalides : la clé '{cle}' est manquante.")
        
        super().__init__()
        self.setWindowTitle("Prédicteur de Pokémon légendaires")
        self.resize(1000, 700)
        self.modele = modele
        self.metadonnees = metadonnees
        self.chemin_historique = chemin_historique
        self._variables = {}
        self._types = {}
        self._nombres = {}
        vbox = QVBoxLayout(self)
        instructions = QLabel("Veuillez choisir les caractéristiques du Pokémon et cliquer sur Prédire pour voir la probabilité qu'il soit légendaire.")
        instructions.setWordWrap(True)
        vbox.addWidget(instructions)
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        self.resultat = QLabel()
        vbox.addWidget(self.resultat)
        
        groupe = QGroupBox("Caractéristiques du Pokémon")
        self.formulaire = self._creer_formulaire(metadonnees, groupe)
        self.bouton = QPushButton("Prédire")
        self.bouton.clicked.connect(self._predire)
        self.formulaire.addRow(self.bouton)
        hbox.addWidget(groupe)
        
        tabwidget = QTabWidget()
        hbox.addWidget(tabwidget, 1)
        
        self.graphique = self._creer_graphique()
        tabwidget.addTab(self.graphique, "Probabilités estimées")
        
        self.historique = self._creer_historique(chemin_historique)
        tabwidget.addTab(self.historique, "Historique des prédictions")
        
    def _creer_formulaire(self, metadonnees: dict, groupe: QGroupBox) -> QFormLayout:
        """Construit le formulaire de saisie à partir des métadonnées."""
        formulaire = QFormLayout(groupe)
        
        for nom in metadonnees["colonnes_categorielles"]:
            liste = QComboBox()
            choix = metadonnees["valeurs_categorielles"][nom]
            liste.addItems(choix)
            liste.setCurrentIndex(0)
            self._types[nom] = liste
            self._variables[nom] = VariableCategorielle(nom, choix)
            formulaire.addRow(nom, liste)
            
        for nom in metadonnees["colonnes_numeriques"]:
            limites = metadonnees["intervalles_numeriques"][nom]
            minimum = int(limites["minimum"])
            maximum = int(limites["maximum"])
            valeur_initiale = (minimum + maximum) // 2
            champ = QLineEdit(str(valeur_initiale))
            self._nombres[nom] = champ
            self._variables[nom] = VariableNumerique(nom, minimum, maximum)
            formulaire.addRow(f"{nom} ({minimum} à {maximum})", champ)
        
        return formulaire
    
    def _creer_graphique(self) -> FigureCanvasQTAgg:
        """Prépare le graphique qui montrera les probabilités prédites."""
        self.figure = Figure(figsize=(5, 3))
        self.axe = self.figure.add_subplot(111)
        self.axe.bar(["Non légendaire", "Légendaire"], [0, 0])
        self.axe.bar_label(self.axe.containers[0], labels=["0.0%", "0.0%"], padding=3)
        self.axe.set_title("Probabilités que le Pokémon soit légendaire")
        self.axe.set_ylabel("Probabilité estimée (%)")
        self.axe.set_ylim(0, 115)
        self.axe.set_yticks([0, 20, 40, 60, 80, 100])
        self.axe.set_xticks([0, 1])
        self.axe.set_xticklabels(["Non légendaire", "Légendaire"])
        return FigureCanvasQTAgg(self.figure)
    
    def _creer_historique(self, chemin_historique: str) -> QListWidget:
        """Construit la liste de l'historique à partir du fichier CSV."""
        liste = QListWidget()
        if not os.path.isfile(chemin_historique):
            return liste
        
        try:
            with open(chemin_historique, "r", encoding="utf-8") as fichier:
                lecteur = csv.DictReader(fichier)
                if lecteur.fieldnames is None:
                    raise HistoriqueErreur("Le fichier d'historique est vide ou n'a pas d'en-têtes.")
                for nom in COLONNES_CARACTERISTIQUES + ["prediction_legendaire", "proba_non_legendaire", "proba_legendaire", "date_heure"]:
                    if nom not in lecteur.fieldnames:
                        raise HistoriqueErreur(f"Le fichier d'historique est invalide : la colonne '{nom}' est manquante.")
                
                for ligne in lecteur:
                    statut = ligne["prediction_legendaire"].strip().lower()

                    if statut not in {"true", "false"}:
                        raise ValueError("Statut de prédiction invalide dans l'historique.")
                    
                    est_legendaire = (statut == "true")
                    resultat = "Légendaire" if est_legendaire else "Non légendaire"
                    cle_probabilite = (
                        "proba_legendaire"
                        if est_legendaire
                        else "proba_non_legendaire"
                    )
                    pourcentage = float(ligne[cle_probabilite])

                    texte = (f"{ligne['date_heure']} : {resultat} ({pourcentage:.1%} estimé)")

                    item = QListWidgetItem(texte)

                    caracteristiques = (self.metadonnees["colonnes_categorielles"] + self.metadonnees["colonnes_numeriques"])
                    details = ""
                    for nom in caracteristiques:
                        if details:
                            details += ", "
                        details += f"{nom} : {ligne[nom]}"
                    item.setToolTip(details)

                    liste.addItem(item)
        except HistoriqueErreur:
            raise
        except (OSError, csv.Error, KeyError, ValueError) as e:
            raise HistoriqueErreur(f"Impossible de lire l'historique : {e}")
        
        return liste
    
    def _predire(self) -> None:
        """Valide la saisie, prédit le statut et actualise l'affichage."""
        valeurs = self._valider()

        if valeurs is None:
            return

        try:
            pokemon = pd.DataFrame([valeurs])
            prediction = bool(self.modele.predict(pokemon)[0])
            probabilites = self.modele.predict_proba(pokemon)[0]
            proba_non_legendaire = probabilites[0]
            proba_legendaire = probabilites[1]

            if prediction:
                texte = "Le modèle prédit que votre Pokémon est légendaire."
                self.resultat.setText(f"{texte}\nProbabilité estimée : {proba_legendaire:.1%}")
            else:
                texte = "Le modèle prédit que votre Pokémon n'est pas légendaire."
                self.resultat.setText(f"{texte}\nProbabilité estimée : {proba_non_legendaire:.1%}")
        except (ValueError, KeyError, TypeError) as e:
            QMessageBox.warning(self, "Erreur de prédiction", f"Le modèle n'a pas pu faire la prédiction : {e}")
            return
        
        try:
            self._actualiser_graphique(proba_non_legendaire, proba_legendaire)
            self._actualiser_historique(valeurs, prediction, proba_non_legendaire, proba_legendaire)
        except HistoriqueErreur as e:
            QMessageBox.warning(self, "Historique non enregistré", f"La prédiction est affichée, mais n'a pas été ajoutée à l'historique.\n{e}")

    def _valider(self) -> dict | None:
        """Retourne les saisies validées ; affiche l'erreur sinon."""
        valeurs = {}

        for nom, variable in self._variables.items():
            if nom in self._types:
                champ = self._types[nom]
                texte = champ.currentText()
            else:
                champ = self._nombres[nom]
                texte = champ.text()

            try:
                valeurs[nom] = variable.valider(texte)
            except DonneeInvalideError as erreur:
                self.resultat.setText(str(erreur))
                champ.setFocus()
                return None

        return valeurs
    
    def _actualiser_graphique(self, proba_non_legendaire: float, proba_legendaire: float) -> None:
        """Met à jour le graphique avec les probabilités de cette saisie."""
        self.axe.clear()
        barres = self.axe.bar(["Non légendaire", "Légendaire"], [proba_non_legendaire * 100, proba_legendaire * 100])
        self.axe.bar_label(barres, labels=[f"{proba_non_legendaire:.1%}", f"{proba_legendaire:.1%}"], padding=3)
        self.axe.set_title("Probabilités que le Pokémon soit légendaire")
        self.axe.set_ylabel("Probabilité estimée (%)")
        self.axe.set_ylim(0, 115)
        self.graphique.draw()
        
    def _actualiser_historique(self, valeurs: dict, prediction: bool, proba_non_legendaire: float, proba_legendaire: float) -> None:
        """Ajoute la prédiction au fichier d'historique CSV."""
        colonnes = (["date_heure"] + self.metadonnees["colonnes_numeriques"] + self.metadonnees["colonnes_categorielles"] + 
        [
        "prediction_legendaire",
        "proba_non_legendaire",
        "proba_legendaire"
        ])

        nouvelle_ligne = {"date_heure": datetime.now().isoformat(timespec="seconds")}
        noms_caracteristiques = (self.metadonnees["colonnes_categorielles"] + self.metadonnees["colonnes_numeriques"])
        for nom in noms_caracteristiques:
            nouvelle_ligne[nom] = valeurs[nom]
        nouvelle_ligne["prediction_legendaire"] = prediction
        nouvelle_ligne["proba_non_legendaire"] = proba_non_legendaire
        nouvelle_ligne["proba_legendaire"] = proba_legendaire
        
        if prediction:
            texte = (f"{nouvelle_ligne['date_heure']} : Légendaire ({proba_legendaire:.1%} estimé)")
        else:
            texte = (f"{nouvelle_ligne['date_heure']} : Non légendaire ({proba_non_legendaire:.1%} estimé)")

        item = QListWidgetItem(texte)
        
        details = ""

        for nom in noms_caracteristiques:
            if details:
                details += ", "
            details += f"{nom} : {valeurs[nom]}"
            item.setToolTip(details)

        self._enregistrer_historique(nouvelle_ligne, colonnes)
        self.historique.addItem(item)

    def _enregistrer_historique(self, nouvelle_ligne: dict, colonnes: list[str]) -> None:
        """Ajoute la prédiction au fichier d'historique CSV."""
        try:
            fichier_non_vide = (os.path.isfile(self.chemin_historique) and os.path.getsize(self.chemin_historique) > 0)
            with open(self.chemin_historique, "a", newline="", encoding="utf-8") as fichier:
                        writer = csv.DictWriter(fichier, fieldnames=colonnes)
                        if not fichier_non_vide:
                            writer.writeheader()
                        writer.writerow(nouvelle_ligne)
        except (OSError, csv.Error, ValueError) as e:
            raise HistoriqueErreur(f"Impossible d'enregistrer la prédiction : {e}")
        

def lancer_interface(modele, metadonnees, chemin_historique: str) -> int:
    """Lance l'interface PyQt6 et retourne son code de sortie."""
    application = QApplication(sys.argv)

    try:
        fenetre = Fenetre(modele, metadonnees, chemin_historique)
    except (DonneeInvalideError, ModeleIndisponibleError, HistoriqueErreur) as e:
        QMessageBox.critical(None, "Impossible de démarrer", str(e))
        return 1
    
    fenetre.show()

    return application.exec()