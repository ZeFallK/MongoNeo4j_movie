# Importation des modules nécessaires
from pymongo import MongoClient
import pandas as pd
import matplotlib, os
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import pearsonr
from dotenv import load_dotenv
load_dotenv()

# Connexion à MongoDB
def connect_to_mongodb():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    return client.entertainment

db = connect_to_mongodb()
films_collection = db.films

# 1. Afficher l'année où le plus grand nombre de films ont été sortis
def question_1():
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]
    result = list(films_collection.aggregate(pipeline))
    return f"Q1: L'année avec le plus de films sortis est {result[0]['_id']} avec {result[0]['count']} films."

# 2. Nombre de films sortis après 1999
def question_2():
    count = films_collection.count_documents({"year": {"$gt": 1999}})
    return f"Q2: Nombre de films sortis après 1999: {count}"

# 3. Moyenne des votes des films sortis en 2007
def question_3():
    pipeline = [
        {"$match": {"year": 2007}},
        {"$group": {"_id": None, "average_votes": {"$avg": "$Votes"}}}
    ]
    result = list(films_collection.aggregate(pipeline))
    if result:
        return f"Q3: La moyenne des votes pour les films de 2007 est: {result[0]['average_votes']:.2f}"
    else:
        return "Aucun film trouvé pour l'année 2007."

# 4. Histogramme du nombre de films par année
def question_4():
    pipeline = [
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    result = list(films_collection.aggregate(pipeline))
    
    years = [doc["_id"] for doc in result if doc["_id"] is not None]
    counts = [doc["count"] for doc in result if doc["_id"] is not None]
    
    #plt.figure(figsize=(12, 6))
    plt.bar(years, counts)
    plt.xlabel('Année')
    plt.ylabel('Nombre de films')
    plt.title('Distribution des films par année')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('assets/question4_histo.png')
    return "Q4: Histogramme généré et sauvegardé sous 'films_par_annee.png'"

# 5. Genres de films disponibles dans la base
def question_5():
    pipeline = [
        {"$project": {"genres": {"$split": ["$genre", ","]}}},
        {"$unwind": "$genres"},
        {"$group": {"_id": "$genres"}},
        {"$sort": {"_id": 1}}
    ]
    genres = [doc["_id"].strip() for doc in films_collection.aggregate(pipeline)]
    return f"Q5: Genres disponibles: {', '.join(genres)}"

# 6. Film qui a généré le plus de revenus
def question_6():
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$exists": True, "$ne": ""}}},
        {"$addFields": {
            "revenue_float": {"$toDouble": "$Revenue (Millions)"}
        }},
        {"$sort": {"revenue_float": -1}},
        {"$limit": 1},
        {"$project": {"_id": 0, "title": 1, "revenue_float": 1, "year": 1}}
    ]
    result = list(films_collection.aggregate(pipeline))
    
    if result:
        film = result[0]
        return (
            f"Q6: Le film qui a généré le plus de revenus est '{film['title']}' "
            f"({film['year']}) avec ${film['revenue_float']:.2f} millions"
        )
    else:
        return "Q6: Aucun film avec revenus trouvé."

# 7. Réalisateurs ayant réalisé plus de 5 films
def question_7():
    pipeline = [
        {"$match": {"Director": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": "$Director", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 5}}},
        {"$sort": {"count": -1}},
        {"$project": {"director": "$_id", "count": 1, "_id": 0}}
    ]
    result = list(films_collection.aggregate(pipeline))
    return [f"{doc['director']} ({doc['count']} films)" for doc in result]

# 8. Genre de film qui rapporte en moyenne le plus de revenus
def question_8():
    pipeline = [
        {"$match": {"Revenue (Millions)": {"$exists": True, "$ne": ""}}},
        {"$addFields": {
            "revenue_float": {"$toDouble": "$Revenue (Millions)"},
            "genres": {"$split": ["$genre", ","]}
        }},
        {"$unwind": "$genres"},
        {"$group": {"_id": {"$trim": {"input": "$genres"}}, "avg_revenue": {"$avg": "$revenue_float"}}},
        {"$sort": {"avg_revenue": -1}},
        {"$limit": 1}
    ]
    result = list(films_collection.aggregate(pipeline))
    if result:
        return f"Q8: Le genre qui rapporte le plus en moyenne est '{result[0]['_id']}' avec ${result[0]['avg_revenue']:.2f} millions"
    else:
        return "Aucun résultat trouvé."

# 9. Les 3 films les mieux notés pour chaque décennie
def question_9():
    decades = [(1990, 1999), (2000, 2009), (2010, 2019)]
    results = {}
    
    for start, end in decades:
        pipeline = [
            {"$match": {"year": {"$gte": start, "$lte": end}, "rating": {"$exists": True, "$ne": ""}}},
            {"$sort": {"rating": -1}},
            {"$limit": 3},
            {"$project": {"_id": 0, "title": 1, "year": 1, "rating": 1}}
        ]
        decade_films = list(films_collection.aggregate(pipeline))
        results[f"{start}-{end}"] = decade_films
    
    return results

# 10. Film le plus long par genre
def question_10():
    pipeline = [
        {"$match": {"Runtime (Minutes)": {"$exists": True, "$ne": ""}}},
        {"$addFields": {
            "runtime_int": {"$toInt": "$Runtime (Minutes)"},
            "genres": {"$split": ["$genre", ","]}
        }},
        {"$unwind": "$genres"},
        {"$addFields": {"genre_trimmed": {"$trim": {"input": "$genres"}}}},
        {"$sort": {"runtime_int": -1}},
        {"$group": {
            "_id": "$genre_trimmed",
            "title": {"$first": "$title"},
            "runtime": {"$first": "$runtime_int"},
            "year": {"$first": "$year"}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = list(films_collection.aggregate(pipeline))
    return [{
        "genre": doc["_id"],
        "film": doc["title"],
        "année": doc["year"],
        "durée": f"{doc['runtime']} minutes"
    } for doc in result]

# 11. Créer une vue MongoDB pour les films bien notés et rentables
def question_11():
    try:
        films_collection.database.command({
            "collMod": "vue_films_premium",  # modifie si existe
            "viewOn": "films",
            "pipeline": [
                {"$match": {
                    "Metascore": {"$gt": 80}, 
                    "Revenue (Millions)": {"$exists": True, "$ne": ""},
                    "$expr": {"$gt": [{"$toDouble": "$Revenue (Millions)"}, 50]}
                }}
            ]
        })
        return "Q11: Vue 'vue_films_premium' modifiée avec succès ✅"
    except:
        try:
            # Si elle n'existe pas
            films_collection.database.command({
                "create": "vue_films_premium",
                "viewOn": "films",
                "pipeline": [
                    {"$match": {
                        "Metascore": {"$gt": 80}, 
                        "Revenue (Millions)": {"$exists": True, "$ne": ""},
                        "$expr": {"$gt": [{"$toDouble": "$Revenue (Millions)"}, 50]}
                    }}
                ]
            })
            return "Q11: Vue 'vue_films_premium' créée avec succès ✅"
        except Exception as e:
            return f"❌ Erreur lors de la création/modification de la vue : {e}"

# 12. Corrélation entre durée et revenu
def question_12():
    pipeline = [
        {"$match": {
            "Runtime (Minutes)": {"$exists": True, "$ne": ""}, 
            "Revenue (Millions)": {"$exists": True, "$ne": ""}
        }},
        {"$addFields": {
            "runtime_int": {"$toInt": "$Runtime (Minutes)"},
            "revenue_float": {"$toDouble": "$Revenue (Millions)"}
        }},
        {"$project": {"_id": 0, "runtime": "$runtime_int", "revenue": "$revenue_float"}}
    ]
    data = list(films_collection.aggregate(pipeline))
    df = pd.DataFrame(data)
    
    # Calcul de la corrélation
    correlation, p_value = pearsonr(df['runtime'], df['revenue'])
    
    # Visualisation
    plt.figure(figsize=(10, 6))
    plt.scatter(df['runtime'], df['revenue'], alpha=0.5)
    plt.title(f'Corrélation entre durée et revenu (r = {correlation:.2f}, p = {p_value:.4f})')
    plt.xlabel('Durée (minutes)')
    plt.ylabel('Revenu (millions $)')
    
    # Ajouter une ligne de tendance
    z = np.polyfit(df['runtime'], df['revenue'], 1)
    p = np.poly1d(z)
    plt.plot(df['runtime'], p(df['runtime']), "r--")
    
    plt.tight_layout()
    plt.savefig('assets/question12_correlation.png')
    
    return {
        "coefficient_correlation": correlation,
        "p_value": p_value,
        "interpretation": "Corrélation positive" if correlation > 0 else "Corrélation négative" if correlation < 0 else "Pas de corrélation",
        "visualisation": "Graphique sauvegardé sous 'correlation_duree_revenu.png'"
    }

# 13. Évolution de la durée moyenne des films par décennie
def question_13():
    # Définir les limites des décennies
    decades = []
    for decade_start in range(1900, 2030, 10):
        decades.append((decade_start, decade_start + 9))
    
    results = []
    for start, end in decades:
        pipeline = [
            {"$match": {
                "year": {"$gte": start, "$lte": end}, 
                "Runtime (Minutes)": {"$exists": True, "$ne": ""}
            }},
            {"$addFields": {"runtime_int": {"$toInt": "$Runtime (Minutes)"}}},
            {"$group": {"_id": None, "avg_runtime": {"$avg": "$runtime_int"}, "count": {"$sum": 1}}},
            {"$project": {"_id": 0, "avg_runtime": 1, "count": 1}}
        ]
        result = list(films_collection.aggregate(pipeline))
        if result and result[0]['count'] > 5:  # Inclure seulement si nous avons assez de films
            results.append({
                "decade": f"{start}-{end}",
                "avg_runtime": result[0]['avg_runtime'],
                "film_count": result[0]['count']
            })
    
    # Visualiser l'évolution
    df = pd.DataFrame(results)
    plt.figure(figsize=(12, 6))
    plt.bar(df['decade'], df['avg_runtime'])
    plt.axhline(y=df['avg_runtime'].mean(), color='r', linestyle='--', label='Moyenne globale')
    plt.xlabel('Décennie')
    plt.ylabel('Durée moyenne (minutes)')
    plt.title('Évolution de la durée moyenne des films par décennie')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('assets/question13_evolution.png')  
    return {
        "data": results,
        "visualisation": "Graphique sauvegardé sous 'evolution_duree_films.png'"
    }

if __name__ == "__main__":
    print(question_1())
    print(question_2())
    print(question_3())
    print(question_4())
    print(question_5())
    print(question_6())
    print(question_7())
    print(question_8())
    print("Question 9:", question_9())
    print("Question 10:", question_10())
    print(question_11())
    print("Question 12:", question_12())
    print("Question 13:", question_13())