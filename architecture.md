# Architecture d'EcoShield AI

## Vue d'Ensemble

EcoShield AI est un système de protection en temps réel conçu pour les infrastructures critiques de la Smart City (eau, électricité). Il utilise une approche hybride d'Intelligence Artificielle pour :

1. **Optimiser la consommation** (Green AI)
2. **Détecter les Cyberattaques** (AI Cybersecurity)

## Flux de Données (Data Pipeline)

### 1. Collecte et Simulation (IoT / Edge)

Les capteurs intelligents envoient des séries temporelles (consommation d'eau en m3, énergie en kW) à la centrale.

- *Technologie :* Génération de données synthétiques réalistes (cycles jour/nuit, pics de demande, saisonnalité).

### 2. Attaques FDI (False Data Injection)

Afin d'éprouver le système, nous simulons trois scenarii d'attaques :

- **Spike Attack** : Injection brutale d'une fausse valeur très élevée.
- **Stealth Attack** : Augmentation progressive et subtile (1% par 1%) pour contourner les seuils d'alerte classiques.
- **Targeted Outage** : Chute brutale à zéro simulant un black-out ou un vol de données de capteurs.

### 3. Modèle IA de Détection (Autoencodeur)

- **Rôle :** The "Watchdog".
- **Architecture :** Un réseau de neurones Autoencodeur basé sur des couches LSTM.
- **Fonctionnement :** Formé uniquement sur des données "propres". En temps réel, il tente de reconstruire la séquence des 24 dernières heures. Si l'erreur de reconstruction (MSE) dépasse un seuil dynamique (99e percentile des erreurs d'entraînement), une anomalie est déclarée.

### 4. Modèle IA de Remplacement (LSTM Forecaster)

- **Rôle :** The "Guardian".
- **Architecture :** Un réseau LSTM de prédiction (Time-Series Forecasting).
- **Fonctionnement :** Dès que l'Autoencodeur signale une donnée corrompue, le LSTM prend le relais. Il analyse les 24 dernières heures saines et prédit la valeur que le capteur *aurait dû* envoyer.
- **Action :** La fausse donnée est rejetée et remplacée par la prédiction du LSTM, assurant la continuité du service sans interruption.

### 5. Optimisation "Green"

En parallèle, le LSTM calcule la consommation de référence et dérive une stratégie d'optimisation (par exemple : réduction de l'éclairage public inutile la nuit, gestion de la pression d'eau) permettant un gain théorique cible de 30%.

### 6. Dashboard (Streamlit)

Une interface visuelle pour la salle de crise affichant :

- Les courbes de consommation (Reçues vs Sécurisées vs Optimisées).
- Les alertes cyber en temps réel.
- Les KPIs : Gain énergétique, Précision de détection, Score de menace.
