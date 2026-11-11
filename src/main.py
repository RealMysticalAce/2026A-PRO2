import matplotlib.pyplot as plt

from .donnees import charger_donnees

donnees = charger_donnees("donnees/pokemon.csv")
plt.bar(["Non-légendaire", "Légendaire"], donnees["Legendary"].value_counts().values)
plt.title("Nombre de Pokémon légendaires vs non légendaires")
plt.xlabel("Légendaire")
plt.ylabel("Nombre de Pokémon")
plt.savefig("modeles/pokemon_legendaires_vs_non_legendaires.png")
plt.show()
