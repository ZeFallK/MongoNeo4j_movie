# 🎬 Projet NoSQL — MongoDB & Neo4j

Ce projet met en œuvre des requêtes sur deux bases NoSQL : **MongoDB** pour les statistiques de films et **Neo4j** pour l’analyse des graphes (films, acteurs, réalisateurs, genres...). Une interface utilisateur a été développée avec **Streamlit** pour permettre une navigation simple à travers les différentes requêtes. Mais il est préférable d'éxecuter chaque fichier manuellement pour de meilleurs résultats

---

## 📁 Arborescence du projet

├── app.py               # Interface utilisateur Streamlit
├── import_data.py       # Script de migration des données MongoDB → Neo4j
├── mongo.py             # Requêtes MongoDB (Questions 1 à 13)
├── cypher.py            # Requêtes Cypher pour Neo4j (Questions 14 à 29)
├── assets/              # Dossier contenant les graphes et visualisations
├── .env                 # Identifiants pour MongoDB & Neo4j
└── requirements.txt     # Liste des dépendances Python

---

## ⚙️ Prérequis

- Python 3.8+
- Un compte MongoDB Atlas avec cluster
- Un compte Neo4j Aura avec base de données active
- Variables d’environnement `.env` :
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>/entertainment 
NEO4J_URI=neo4j+s://<host> 
NEO4J_USER=neo4j 
NEO4J_PASSWORD=<mot_de_passe>

------

## 🚀 **Exécution locale (recommandée)**

> 💡 Tester localement garantit une meilleure performance, surtout pour les graphiques générés.

### Étapes :

1. **Cloner le dépôt**

```bash
git clone https://github.com/ton-pseudo/projet-nosql.git
cd projet-nosql
python -m venv venv
source venv/bin/activate  # Sur Windows : .\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py 
```
---
## 📊 Données utilisées

Les données concernent environ **1000 films** et incluent :

- **Informations générales** : titre, année, genres  
- **Statistiques** : durée, score, votes  
- **Personnes clés** : réalisateurs, acteurs  
- **Performance** : revenus générés (en millions)

---

✍️ Auteurs
Alpha, Garance, Alexis — Étudiants à l'ESIEA
