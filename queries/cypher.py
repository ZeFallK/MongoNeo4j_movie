from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def run_query(query, parameters=None):
    with neo4j_driver.session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]

def question_14():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    RETURN a.name AS acteur, COUNT(f) AS nb_films
    ORDER BY nb_films DESC
    LIMIT 1
    """
    result = run_query(query)
    return f"Q14: Acteur ayant joué dans le plus de films : {result[0]['acteur']} ({result[0]['nb_films']} films)"

def question_15():
    query = """
    MATCH (anne:Actor {name: "Anne Hathaway"})-[:A_JOUE]->(f:Film)<-[:A_JOUE]-(coacteur:Actor)
    WHERE anne <> coacteur
    RETURN DISTINCT coacteur.name AS acteur
    ORDER BY acteur
    """
    result = run_query(query)
    return f"Q15: Acteurs ayant joué avec Anne Hathaway : {[r['acteur'] for r in result]}"

def question_16():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)
    WHERE f.revenue IS NOT NULL AND f.revenue <> ""
    RETURN a.name AS acteur, SUM(toFloat(f.revenue)) AS total_revenue
    ORDER BY total_revenue DESC
    LIMIT 1
    """
    result = run_query(query)
    r = result[0]
    return f"Q16: {r['acteur']} avec un total de revenus de ${r['total_revenue']:.2f}M"
    
def question_17():
    query = """
    MATCH (f:Film)
    RETURN avg(f.votes) AS moyenne_votes
    """
    result = run_query(query)
    return f"Q17: Moyenne des votes : {result[0]['moyenne_votes']:.2f}"

def question_18():
    query = """
    MATCH (f:Film)-[:APPARTIENT_A]->(g:Genre)
    RETURN g.name AS genre, COUNT(f) AS nb_films
    ORDER BY nb_films DESC
    LIMIT 1
    """
    result = run_query(query)
    r = result[0]
    return f"Q18: Genre le plus représenté : {r['genre']} ({r['nb_films']} films)"
    
def question_20():
    query = """
    MATCH (r:Realisateur)-[:A_REALISE]->(f:Film)<-[:A_JOUE]-(a:Actor)
    RETURN r.name AS realisateur, COUNT(DISTINCT a) AS nb_acteurs
    ORDER BY nb_acteurs DESC
    LIMIT 1
    """
    result = run_query(query)
    r = result[0]
    return f"Q20: Réalisateur ayant travaillé avec le plus d’acteurs : {r['realisateur']} ({r['nb_acteurs']} acteurs)"
    
def question_21():
    query = """
    MATCH (f1:Film)<-[:A_JOUE]-(a:Actor)-[:A_JOUE]->(f2:Film)
    WHERE f1 <> f2
    RETURN f1.title AS film, COUNT(DISTINCT a) AS nb_acteurs_communs
    ORDER BY nb_acteurs_communs DESC
    LIMIT 5
    """
    result = run_query(query)
    return "Q21: Films les plus connectés : " + ", ".join([f"{r['film']} ({r['nb_acteurs_communs']} acteurs en commun)" for r in result])
    
def question_22():
    query = """
    MATCH (a:Actor)-[:A_JOUE]->(f:Film)<-[:A_REALISE]-(r:Realisateur)
    RETURN a.name AS acteur, COUNT(DISTINCT r) AS nb_realisateurs
    ORDER BY nb_realisateurs DESC
    LIMIT 5
    """
    result = run_query(query)
    return "Q22: Top 5 acteurs par nb de réalisateurs différents : " + ", ".join([f"{r['acteur']} ({r['nb_realisateurs']})" for r in result])
    
def question_23():
    query = """
    MATCH (a:Actor {name: "Chris Pratt"})-[:A_JOUE]->(:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH a, COLLECT(DISTINCT g) AS genres_pref
    MATCH (f:Film)-[:APPARTIENT_A]->(g2:Genre)
    WHERE g2 IN genres_pref AND NOT (a)-[:A_JOUE]->(f)
    RETURN DISTINCT f.title AS film
    LIMIT 5
    """
    result = run_query(query)
    return "Q23: Recommandations de films pour Chris Pratt : " + ", ".join([r['film'] for r in result])
    
def question_24():
    query = """
    MATCH (r1:Realisateur)-[:A_REALISE]->(:Film)-[:APPARTIENT_A]->(g:Genre)<-[:APPARTIENT_A]-(:Film)<-[:A_REALISE]-(r2:Realisateur)
    WHERE r1 <> r2
    MERGE (r1)-[:INFLUENCE_PAR]->(r2)
    """
    run_query(query)
    return "Q24: Relations INFLUENCE_PAR créées entre réalisateurs selon genres similaires."
    
def question_25():
    actor1 = "Chris Evans"
    actor2 = "Scarlett Johansson" 
    query = """
    MATCH (a1:Actor {name: $actor1}), (a2:Actor {name: $actor2})
    MATCH path = shortestPath((a1)-[:A_JOUE*]-(a2))
    RETURN path
    """
    result = run_query(query, {"actor1": actor1, "actor2": actor2})
    if result:
        return f"Q25: Chemin le plus court entre {actor1} et {actor2} trouvé."
    else:
        return f"Q25: Aucun chemin trouvé entre {actor1} et {actor2}."

def question_27():
    query = """
    MATCH (f1:Film)-[:APPARTIENT_A]->(g:Genre)<-[:APPARTIENT_A]-(f2:Film)
    WHERE f1 <> f2
    AND f1.director <> f2.director
    RETURN DISTINCT f1.title AS film1, f2.title AS film2, g.name AS genre
    LIMIT 10
    """
    result = run_query(query)
    return "Q27: Films avec genres en commun mais réalisateurs différents : " + ", ".join([f"{r['film1']} / {r['film2']} ({r['genre']})" for r in result])
def question_28():
    actor_name = "Brad Pitt"  # à adapter
    query = """
    MATCH (a:Actor {name: $actor_name})-[:A_JOUE]->(:Film)-[:APPARTIENT_A]->(g:Genre)
    WITH a, COLLECT(DISTINCT g) AS genres_pref
    MATCH (f:Film)-[:APPARTIENT_A]->(g2:Genre)
    WHERE g2 IN genres_pref AND NOT (a)-[:A_JOUE]->(f)
    RETURN DISTINCT f.title AS film
    LIMIT 5
    """
    result = run_query(query, {"actor_name": actor_name})
    return f"Q28: Films recommandés à {actor_name} : " + ", ".join([r['film'] for r in result])
def question_29():
    query = """
    MATCH (r1:Realisateur)-[:A_REALISE]->(f1:Film)-[:APPARTIENT_A]->(g:Genre)<-[:APPARTIENT_A]-(f2:Film)<-[:A_REALISE]-(r2:Realisateur)
    WHERE r1 <> r2 AND f1.year = f2.year
    MERGE (r1)-[:CONCURRENCE]->(r2)
    """
    run_query(query)
    return "Q29: Relations CONCURRENCE créées entre réalisateurs."

if __name__ == "__main__":
    print(question_14())
    print(question_15())
    print(question_16())
    print(question_17())
    print(question_18())
    print(question_20())
    print(question_21())
    print(question_22())
    print(question_23())
    print(question_24())
    print(question_25())
    print(question_27())
    print(question_28())
    print(question_29())