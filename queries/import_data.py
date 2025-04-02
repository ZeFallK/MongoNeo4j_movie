from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
load_dotenv()

# Connexion MongoDB
print("Connexion à MongoDB...")
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
collection = mongo_client["entertainment"]["films"]
print("Connexion MongoDB établie avec succès!")
# Connexion Neo4j
print("Connexion à Neo4j...")
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password =  os.getenv("NEO4J_PASSWORD")
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
print("Connexion Neo4j faite")

# Exécuter une requête Cypher avec retour d'information
def execute_query(query, parameters=None):
    with neo4j_driver.session() as session:
        result = session.run(query, parameters or {})
        return result.consume().counters
#Nettoyage de la base Neo4j
execute_query("MATCH (n) DETACH DELETE n")
# Récupérer tous les films
print("Récupération des films depuis MongoDB...")
films = list(collection.find({}, {
    "_id": 1,
    "title": 1,
    "year": 1,
    "Votes": 1,
    "Revenue (Millions)": 1,
    "rating": 1,
    "Director": 1,
    "Actors": 1,
    "genre": 1,
    "Description": 1,
    "Runtime (Minutes)": 1
}))
print(f"Récupération terminée: {len(films)} films trouvés.")
# 1. Créer des noeuds de type films avec uniquement les champs demandés
print("\nÉTAPE 1: Création des nœuds Films...")
films_count = 0
for film in films:
    counters = execute_query("""
        MERGE (f:Film {id: $id})
        SET f.title = $title, 
            f.year = $year, 
            f.votes = $votes, 
            f.revenue = $revenue, 
            f.rating = $rating,
            f.director = $director
    """, {
        "id": str(film["_id"]),
        "title": film.get("title", "Unknown"),
        "year": film.get("year", 0),
        "votes": film.get("Votes", 0),
        "revenue": film.get("Revenue (Millions)", 0),
        "rating": film.get("rating", "N/A"),
        "director": film.get("Director", "Unknown")
    })  
    if counters.nodes_created > 0:
        films_count += 1
print(f"ÉTAPE 1 terminée: {films_count} nœuds Films créés.")

# 2. Créer des noeuds de type Actors contenant uniquement les acteurs distincts
print("\nÉTAPE 2: Création des nœuds Actors...")
actors_count = 0
for film in films:
    if "Actors" in film and film["Actors"]:
        for actor in film["Actors"].split(", "):
            counters = execute_query("""
                MERGE (a:Actor {name: $actor})
                RETURN a
            """, {
                "actor": actor
            })            
            if counters.nodes_created > 0:
                actors_count += 1
print(f"ÉTAPE 2 terminée: {actors_count} nœuds Actors créés.")

# 3. Créer des relations "A_JOUE" entre acteurs et films
print("\nÉTAPE 3: Création des relations A_JOUE...")
relations_count = 0
for film in films:
    if "Actors" in film and film["Actors"]:
        for actor in film["Actors"].split(", "):
            counters = execute_query("""
                MATCH (a:Actor {name: $actor})
                MATCH (f:Film {id: $film_id})
                MERGE (a)-[r:A_JOUE]->(f)
                RETURN r
            """, {
                "actor": actor,
                "film_id": str(film["_id"])
            })            
            if counters.relationships_created > 0:
                relations_count += 1
print(f"ÉTAPE 3 terminée: {relations_count} relations A_JOUE créées.")

# 4. Créer des noeuds pour les membres du projet et les attacher chacun à un film spécifique
print("\nÉTAPE 4: Création des nœuds pour les membres du projet...")
membre_to_film = {
    "Alpha": "Rogue One",
    "Garance": "Arrival",
    "Alexis": "Sully"
}
membres_count = 0
for membre, film_choisi in membre_to_film.items():
    # Vérifier que le film existe (facultatif)
    film_exists = execute_query("""
        MATCH (f:Film {title: $title})
        RETURN count(f) as count
    """, {"title": film_choisi})
    # Créer le noeud acteur et relation
    counters = execute_query("""
        MERGE (a:Actor {name: $name})
        WITH a
        MATCH (f:Film {title: $title})
        MERGE (a)-[r:A_JOUE]->(f)
        RETURN a, r
    """, {
        "name": membre,
        "title": film_choisi
    })
    if counters.nodes_created > 0:
        membres_count += 1
print(f"ÉTAPE 4 terminée: {membres_count} membres du projet ajoutés et reliés à leurs films respectifs.")

# 5. Créer des nœuds de type Realisateur depuis le champ Director
print("\nÉTAPE 5: Création des nœuds Realisateur...")
realisateurs_count = 0
for film in films:
    if "Director" in film and film["Director"]:
        counters = execute_query("""
            MERGE (r:Realisateur {name: $name})
            WITH r
            MATCH (f:Film {id: $film_id})
            MERGE (r)-[rel:A_REALISE]->(f)
            RETURN r, rel
        """, {
            "name": film["Director"],
            "film_id": str(film["_id"])
        })        
        if counters.nodes_created > 0:
            realisateurs_count += 1

print(f"ÉTAPE 5 terminée: {realisateurs_count} nœuds Realisateur créés.")

# Bonus: Ajout des genres (mentionné dans l'énoncé)
print("\nBONUS: Création des nœuds Genre et relations APPARTIENT_A...")
genres_count = 0
genre_relations = 0

for film in films:
    if "genre" in film and film["genre"]:
        genres = [g.strip() for g in film["genre"].split(",")]
        for genre in genres:
            # Créer le nœud Genre
            genre_counters = execute_query("""
                MERGE (g:Genre {name: $genre})
                RETURN g
            """, {
                "genre": genre
            })        
            if genre_counters.nodes_created > 0:
                genres_count += 1             
            # Créer la relation entre Film et Genre
            rel_counters = execute_query("""
                MATCH (g:Genre {name: $genre})
                MATCH (f:Film {id: $film_id})
                MERGE (f)-[r:APPARTIENT_A]->(g)
                RETURN r
            """, {
                "genre": genre,
                "film_id": str(film["_id"])
            })            
            if rel_counters.relationships_created > 0:
                genre_relations += 1
print(f"BONUS terminé: {genres_count} nœuds Genre créés et {genre_relations} relations APPARTIENT_A créées.")
# Fermeture des connexions
neo4j_driver.close()
mongo_client.close()
print(f"- {films_count} Films")
print(f"- {actors_count} Actors")
print(f"- {relations_count} relations A_JOUE")
print(f"- {membres_count} membres du projet")
print(f"- {realisateurs_count} Realisateurs")
print(f"- {genres_count} Genres")