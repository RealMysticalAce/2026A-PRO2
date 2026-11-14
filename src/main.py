import matplotlib.pyplot as plt
import pandas as pd

from .donnees import JeuDonnees
from .modele import Modele

donnees = JeuDonnees("donnees/pokemon.csv").donnees
plt.bar(["Non-légendaire", "Légendaire"], donnees["Legendary"].value_counts().values)
plt.title("Nombre de Pokémon légendaires vs non légendaires")
plt.xlabel("Légendaire")
plt.ylabel("Nombre de Pokémon")
plt.savefig("modeles/pokemon_legendaires_vs_non_legendaires.png")
plt.show()

jeu = JeuDonnees("donnees/Pokemon.csv")
modele = Modele(jeu.x, jeu.y)
modele.entrainer()
modele.evaluer()
modele.sauvegarder("modeles")

nouveau_pokemon = pd.DataFrame([{
    "Type 1": "Psychic",
    "Type 2": "Aucun",
    "HP": 106,
    "Attack": 110,
    "Defense": 90,
    "Sp. Atk": 154,
    "Sp. Def": 90,
    "Speed": 130,
    "Generation": 1,
}])
resultat = modele.predire(nouveau_pokemon)
if resultat:
    print("Le modèle prédit : légendaire")
else:
    print("Le modèle prédit : non légendaire")
    
nouveau_pokemon2 = pd.DataFrame([{
    "Type 1": "Grass",
    "Type 2": "Poison",
    "HP": 45,
    "Attack": 49,
    "Defense": 49,
    "Sp. Atk": 65,
    "Sp. Def": 65,
    "Speed": 45,
    "Generation": 1,
}])
resultat2 = modele.predire(nouveau_pokemon2)
if resultat2:
    print("Le modèle prédit : légendaire")
else:
    print("Le modèle prédit : non légendaire") 