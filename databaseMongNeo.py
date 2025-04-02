import os
from dotenv import load_dotenv
from pymongo import MongoClient
from neo4j import GraphDatabase

load_dotenv()

# --- MongoDB ---
def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    db = client["entertainment"]
    return db["films"]

# --- Neo4j ---
def get_neo4j_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    return GraphDatabase.driver(uri, auth=(user, password))

def run_query(query, params=None):
    with get_neo4j_driver().session() as session:
        return [record.data() for record in session.run(query, params or {})]
