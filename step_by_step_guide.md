# Guide d'Implémentation Étape par Étape - EcoShield AI

Ce guide vous expliquera comment configurer votre environnement, lancer les modèles et démarrer la démonstration du Dashboard EcoShield AI.

## Prérequis

Assurez-vous d'avoir Python 3.8+ installé sur votre machine.

## Étape 1 : Installation des Dépendances

Ouvrez un terminal ou une invite de commande dans le dossier du projet (`c:/EcoShield_AI`) et exécutez la commande suivante :

```bash
pip install -r requirements.txt
```

## Étape 2 : Entraînement des Modèles

Avant de lancer le Dashboard, les modèles d'IA doivent être entraînés sur des données saines.

1. Toujours dans le terminal, exécutez :

   ```bash
   python models.py
   ```

2. **Ce que fait ce script :**
   - Il génère automatiquement 60 jours de données synthétiques saines via `data_generation.py`.
   - Il entraîne le modèle `LSTM Forecaster` pour la prédiction de consommation.
   - Il entraîne le modèle `Autoencoder` pour la détection d'anomalies.
   - Il calcule le seuil dynamique d'anomalie et sauvegarde les poids des modèles (`.pth`), ainsi que les paramètres de normalisation (`.npy`, `.txt`).
3. Attendez que le script affiche *Training complete. Models and parameters saved.*

## Étape 3 : Lancement du Dashboard Streamlit

Une fois l'entraînement terminé, vous pouvez lancer l'interface graphique en temps réel.

1. Exécutez la commande :

   ```bash
   streamlit run app.py
   ```

2. Votre navigateur web s'ouvrira automatiquement (généralement sur `http://localhost:8501`).

## Étape 4 : Utilisation du Dashboard (Simulation)

1. **Interface Principale :** Vous verrez le Dashboard prêt à démarrer. Au départ, aucune courbe n'est affichée dynamique, seul l'état "Système Prêt" est visible.
2. **Configuration :** Dans la barre latérale gauche (Sidebar), vous pouvez ajuster la *Vitesse de Simulation* (en millisecondes) pour accélérer ou ralentir l'arrivée des nouvelles données.
3. **Démarrage :** Cliquez sur le bouton bleu **"Démarrer la Simulation en Temps Réel"**.
4. **Observation :**
   - Les données (propres au début, puis attaquées plus tard) vont commencer à défiler heure par heure.
   - L'Autoencodeur calculera l'erreur de reconstruction en direct. S'il détecte un "Spike", un "Stealth", ou une "Targeted Outage", une alerte rouge sera affichée.
   - La courbe bleue (Signal Sécurisé) continuera de manière fluide car le LSTM remplacera la valeur piratée en temps réel.
   - La courbe verte montrera le "Gain Énergétique" simulé.
   - Les KPIs en haut (Niveau de Menace, Précision, Rappel) se mettront à jour dynamiquement selon les performances réelles du modèle face aux attaques injectées.

## Structure des Fichiers

- `data_generation.py` : Module de création des séries temporelles simulées.
- `models.py` : Définition des réseaux de neurones (PyTorch) et boucles d'entraînement.
- `simulation.py` : Logique d'injection des attaques FDI.
- `app.py` : Le code du Dashboard interactif Streamlit.
- Fichiers `.md` : Documentation pour le Pitch, l'Architecture et le Scénario de Démo.
