"""Premier prototype PyQt6, alimenté seulement par Pokemon.csv."""

import os
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from .donnees import COLONNES_CATEGORIELLES, COLONNES_NUMERIQUES, JeuDonnees


def creer_graphique(jeu: JeuDonnees) -> FigureCanvasQTAgg:
    """Construit le graphique des statuts déjà connus dans le CSV."""
    figure = Figure(figsize=(4.6, 3.3), layout="constrained")
    axe = figure.add_subplot(111)

    non_legendaires = int(jeu.y.eq(False).sum())
    legendaires = int(jeu.y.eq(True).sum())

    barres = axe.bar(
        ["Non légendaire", "Légendaire"],
        [non_legendaires, legendaires],
        color=["#307a86", "#d89529"],
    )
    axe.bar_label(barres, padding=3)
    axe.set(
        title="Répartition dans le CSV",
        xlabel="Statut",
        ylabel="Nombre de formes",
        ylim=(0, max(non_legendaires, legendaires) * 1.15),
    )

    return FigureCanvasQTAgg(figure)


class Fenetre(QWidget):
    """Affiche un formulaire et le graphique exploratoire."""

    def __init__(self, jeu: JeuDonnees) -> None:
        """Construit la fenêtre à partir des données déjà nettoyées."""
        super().__init__()
        self.setWindowTitle("Pokémon — Prototype sans modèle")
        self.resize(780, 440)

        self._nombres: dict[str, tuple[QLineEdit, int, int]] = {}
        self._types: dict[str, QComboBox] = {}

        page = QVBoxLayout(self)
        page.addWidget(
            QLabel("Ce prototype vérifie le profil. Il ne fait pas de prédiction.")
        )

        contenu = QHBoxLayout()
        page.addLayout(contenu, 1)

        groupe = QGroupBox("Profil du Pokémon")
        formulaire = QFormLayout(groupe)
        contenu.addWidget(groupe)
        contenu.addWidget(creer_graphique(jeu), 1)

        # Un champ de texte par statistique, avec ses bornes tirées du CSV.
        for nom in COLONNES_NUMERIQUES:
            colonne = jeu.x[nom]
            minimum = int(colonne.min())
            maximum = int(colonne.max())

            champ = QLineEdit(str(int(colonne.median())))
            self._nombres[nom] = (champ, minimum, maximum)
            formulaire.addRow(f"{nom} ({minimum} à {maximum})", champ)

        # Une liste déroulante par colonne de type.
        for nom in COLONNES_CATEGORIELLES:
            liste = QComboBox()
            choix = sorted(
                valeur for valeur in jeu.x[nom].dropna().unique() if valeur
            )
            liste.addItems(choix)
            self._types[nom] = liste
            formulaire.addRow(nom, liste)

        bouton = QPushButton("Vérifier les saisies")
        bouton.clicked.connect(self._verifier)
        formulaire.addRow(bouton)

        self._message = QLabel()
        self._message.setWordWrap(True)
        page.addWidget(self._message)

    def _verifier(self) -> None:
        """Affiche la première erreur ou confirme que le profil est valide."""
        for nom, (champ, minimum, maximum) in self._nombres.items():
            try:
                valeur = int(champ.text().strip())
            except ValueError:
                self._message.setText(f"{nom} : entre un nombre entier.")
                champ.setFocus()
                return

            if not minimum <= valeur <= maximum:
                self._message.setText(
                    f"{nom} : entre une valeur de {minimum} à {maximum}."
                )
                champ.setFocus()
                return

        for nom, liste in self._types.items():
            if not liste.currentText():
                self._message.setText(f"{nom} : choisis un type.")
                return

        self._message.setText("Profil valide. Aucun modèle n’est encore chargé.")


def main() -> int:
    """Charge le CSV puis ouvre la fenêtre; retourne 1 si la lecture échoue."""
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chemin = os.path.join(racine, "donnees", "Pokemon.csv")

    if not os.path.isfile(chemin):
        print(f"CSV introuvable : {chemin}", file=sys.stderr)
        return 1

    try:
        jeu = JeuDonnees(chemin)
    except (OSError, ValueError, KeyError) as erreur:
        print(f"Impossible de charger le CSV : {erreur}", file=sys.stderr)
        return 1

    application = QApplication(sys.argv[:1])
    fenetre = Fenetre(jeu)
    fenetre.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())