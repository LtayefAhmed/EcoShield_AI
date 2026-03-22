# 🛡️ EcoShield AI

> **La Smart City sous haute protection — Optimisation Green & Cybersécurité en temps réel**

---

## 🎬 Démo Vidéo

> 🔗 **Lien direct :** [Watch the demo on Google Drive](https://drive.google.com/file/d/13LsQyQvF2Jpe8gV-gwtT7_ck7qsNChBg/view?usp=sharing)

---

## 📖 Description

**EcoShield AI** est un système de protection en temps réel conçu pour les infrastructures critiques de la Smart City (eau, électricité). Il utilise une approche hybride d'Intelligence Artificielle pour :

- 🌿 **Optimiser la consommation énergétique** (Green AI) — jusqu'à **30% d'économie**
- 🔒 **Détecter et neutraliser les cyberattaques** (AI Cybersecurity) — précision de **99%**

---

## 🏗️ Architecture

```
Capteurs IoT ──► Autoencodeur LSTM (Détection) ──► LSTM Forecaster (Correction) ──► Dashboard Streamlit
                     │                                      │
                     ▼                                      ▼
              🚨 Alerte Cyber                     🔄 Donnée corrigée
                                                  📉 Optimisation Green
```

### Modèles IA

| Modèle | Rôle | Description |
|--------|------|-------------|
| **Autoencodeur LSTM** | 🐕 The Watchdog | Détecte les anomalies par erreur de reconstruction (MSE > seuil dynamique au 99e percentile) |
| **LSTM Forecaster** | 🛡️ The Guardian | Prédit et remplace les données corrompues en temps réel |

### Types d'attaques simulées

- **Spike Attack** — Injection brutale d'une fausse valeur très élevée
- **Stealth Attack** — Augmentation progressive et subtile (+1% par pas)
- **Targeted Outage** — Chute brutale à zéro (simulation de black-out)

---

## 🖥️ Dashboard

Le dashboard Streamlit affiche en temps réel :

- 📈 Courbes de consommation : **Reçues** vs **Sécurisées** vs **Optimisées**
- 🚨 Alertes cyber en temps réel
- 📊 KPIs : Gain énergétique, Précision de détection, Score de menace

---

## 🚀 Installation & Lancement

### Prérequis

- Python 3.8+
- pip

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/LtayefAhmed/EcoShield_AI.git
cd EcoShield_AI

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
# Lancer le dashboard
streamlit run app.py
```

---

## 📁 Structure du Projet

```
EcoShield_AI/
├── app.py                    # Application Streamlit (Dashboard)
├── models.py                 # Définition des modèles IA (Autoencodeur + LSTM)
├── simulation.py             # Simulation des attaques FDI
├── data_generation.py        # Génération de données synthétiques réalistes
├── EcoShield_AI_Core.ipynb   # Notebook d'entraînement des modèles
├── autoencoder.pth           # Poids du modèle Autoencodeur
├── lstm_forecaster.pth       # Poids du modèle LSTM Forecaster
├── anomaly_threshold.txt     # Seuil de détection d'anomalies
├── scaler_min.npy            # Paramètres de normalisation (min)
├── scaler_max.npy            # Paramètres de normalisation (max)
├── requirements.txt          # Dépendances Python
├── architecture.md           # Documentation de l'architecture
├── demo_scenario.md          # Scénario de démonstration
├── pitch_deck.md             # Notes pour le pitch
└── README.md                 # Ce fichier
```

---

## 🛠️ Technologies Utilisées

| Technologie | Usage |
|-------------|-------|
| **Python** | Langage principal |
| **PyTorch** | Modèles de Deep Learning (Autoencodeur & LSTM) |
| **Streamlit** | Dashboard interactif |
| **Plotly** | Visualisations dynamiques |
| **Pandas / NumPy** | Manipulation des données |
| **Scikit-learn** | Prétraitement et métriques |

---

## 👥 Équipe

> _Ajoutez ici les membres de votre équipe_

---

## 📄 Licence

Ce projet a été développé dans le cadre d'un hackathon.
