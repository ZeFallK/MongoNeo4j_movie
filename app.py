import streamlit as st
from queries.mongo import (
    question_1, question_2, question_3, question_4,
    question_5, question_6, question_7, question_8,
    question_9, question_10, question_11,
    question_12, question_13
)
from queries.cypher import (
    question_14, question_15, question_16,
    question_17, question_18, question_20,
    question_21, question_22, question_23,
    question_24, question_25, question_27,
    question_28, question_29
)

st.set_page_config(page_title="Projet MongoDB & Neo4j", layout="wide")

# Header
st.markdown("<h1 style='text-align: center;'>🎬 Projet NoSQL - MongoDB & Neo4j</h1>", unsafe_allow_html=True)
st.markdown("---")

# Liste des questions disponibles
questions = {
    # MongoDB
    "Q1. Année avec le plus de films": question_1,
    "Q2. Films après 1999": question_2,
    "Q3. Moyenne des votes en 2007": question_3,
    "Q4. Histogramme films par année": question_4,
    "Q5. Genres disponibles": question_5,
    "Q6. Film le plus rentable": question_6,
    "Q7. Réalisateurs prolifiques": question_7,
    "Q8. Genre le plus rentable": question_8,
    "Q9. Top films par décennie": question_9,
    "Q10. Film le plus long par genre": question_10,
    "Q11. Création vue MongoDB": question_11,
    "Q12. Corrélation durée/revenu": question_12,
    "Q13. Évolution durée par décennie": question_13,

    # Neo4j
    "Q14. Acteur avec le plus de films": question_14,
    "Q15. Acteurs avec Anne Hathaway": question_15,
    "Q16. Acteur avec le plus de revenus": question_16,
    "Q17. Moyenne des votes (Neo4j)": question_17,
    "Q18. Genre le plus représenté": question_18,
    "Q20. Réalisateur avec + d’acteurs": question_20,
    "Q21. Films les plus connectés": question_21,
    "Q22. Acteurs avec le + de réalisateurs": question_22,
    "Q23. Reco à un acteur par genre": question_23,
    "Q24. Création de relation INFLUENCE_PAR": question_24,
    "Q25. Chemin entre deux acteurs": question_25,
    "Q27. Films avec le plus d’acteurs": question_27,
    "Q28. Films avec le plus de genres": question_28,
    "Q29. Films avec le plus de réalisateurs": question_29
}

# Sidebar : sélection d’une question
selected = st.sidebar.selectbox("📌 Sélectionne une question", list(questions.keys()))
result = questions[selected]()
st.subheader(selected)

# Affichage dynamique des résultats
def afficher_resultat(res):
    if isinstance(res, str):
        st.write(res)
    elif isinstance(res, list):
        for item in res:
            st.write("•", item)
    elif isinstance(res, dict):
        # Cas spécial : chaque clé a une liste de films (ex: Q9)
        if all(isinstance(v, list) for v in res.values()):
            for k, lst in res.items():
                st.markdown(f"**{k}**")
                for item in lst:
                    st.write("-", item)
        else:
            for k, v in res.items():
                if isinstance(v, str) and "png" in v:
                    st.image(v, use_column_width=True)
                else:
                    st.write(f"**{k.replace('_', ' ').capitalize()}**: {v}")

afficher_resultat(result)

# Option pour tout afficher
if st.sidebar.checkbox("Afficher toutes les questions"):
    st.markdown("---")
    for key, func in questions.items():
        st.subheader(key)
        res = func()
        afficher_resultat(res)
        st.markdown("---")
