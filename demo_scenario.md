# Demo Scenario Script 🎬

## Préparation (Avant le Pitch)

1. Ouvrez un terminal et assurez-vous que les modèles sont entraînés : `python models.py`.
2. Lancez le dashboard Streamlit : `streamlit run app.py`.
3. Partagez l'écran sur le Dashboard. Ne cliquez pas encore sur "Démarrer".

## Déroulement de la Démo (Pendant le Pitch)

### 1. Introduction (0:00 - 0:30)

- **Action :** Affichez la page d'accueil du Dashboard ("Système Prêt").
- **Parole :** *"Bienvenue dans le centre de contrôle d'EcoShield AI. Actuellement, notre ville respire normalement."*

### 2. Lancement & Situation Normale (0:30 - 1:00)

- **Action :** Cliquez sur le bouton "Démarrer la Simulation en Temps Réel".
- **Parole :** *"Je lance la simulation. L'IA de prédiction (la courbe verte) calcule la consommation idéale et nous fait économiser près de 30% d'énergie. La courbe pointillée orange représente les données brutes envoyées par les capteurs."*
- **Action :** Laissez tourner quelques secondes. Montrez que le badge vert "Système Normal" s'affiche et que les courbes bleues et oranges se superposent (pas d'attaque).

### 3. L'Attaque Spike (1:00 - 1:30)

- **Action :** Laissez le temps s'écouler jusqu'à ce que la première attaque Spike (le pic brutal) arrive sur le graphique.
- **Parole :** *"Attention, voici notre premier incident cyber. Un hacker vient d'injecter un pic de fausse consommation pour faire sauter le réseau. Regardez ! L'alerte rouge s'est déclenchée instantanément."*
- **Action :** Pointez la croix rouge (X) sur le graphique et montrez que la ligne bleue (EcoShield) coupe le pic et reste lisse en se basant sur la prédiction IA.
- **Parole :** *"Le système a ignoré le capteur piraté et a remplacé la donnée par la prédiction de notre IA. La ville n'a rien senti."*

### 4. L'Attaque Stealth (1:30 - 2:00)

- **Action :** Attendez l'attaque furtive sur le graphique de l'eau.
- **Parole :** *"Les pics sont faciles à voir. Mais regardez le graphe de l'eau. C'est une attaque furtive. Le hacker augmente la pression goutte à goutte. Un système classique ne verrait rien. Mais notre Autoencodeur détecte cette subtile déviation et rétablit la donnée saine."*
- **Action :** Laissez la démo tourner pour voir les statistiques (Précision, Rappel) s'ajuster en temps réel.

### 5. Conclusion (2:00 - 2:15)

- **Action :** Montrez les KPIs (Gain énergétique, Niveau de menace).
- **Parole :** *"EcoShield AI optimise nos ressources tout en neutralisant les menaces en temps réel. Merci de votre attention."*
