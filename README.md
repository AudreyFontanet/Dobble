# Dobble Custom Card Generator

Ce script Python génère un jeu de cartes Dobble personnalisé à partir d’un dossier d’images. Il crée un PDF prêt à imprimer (format A4), avec 6 cartes par page, comprenant des marques de découpe et des layouts aléatoires (taille, rotation, position) pour chaque symbole.

---

## Fonctionnalités

- Supporte différentes versions du jeu Dobble avec `p` égal à 2, 3, 5 ou 7.
- Charge automatiquement les `p+1` images depuis un dossier donné.
- Génère des cartes Dobble avec symboles disposés dans des zones variées en taille, position et rotation.
- Ajoute des marques noires autour des zones pour faciliter la découpe.
- Crée un fichier PDF format A4 avec 6 cartes par page et lignes guides pour la découpe.
- Sauvegarde les cartes PNG individuelles et des images de debug montrant les layouts utilisés.

---

## Prérequis

- Python 3.x
- Bibliothèques Python:
  - Pillow (`pip install pillow`)
  - FPDF (`pip install fpdf`)

---

## Installation

1. Copier le script `dobble_generator.py`.
2. Installer les dépendances :

```bash
pip install pillow fpdf
