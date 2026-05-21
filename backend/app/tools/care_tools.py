from langchain_core.tools import tool

@tool
def recommend_interim_care(recommendation: str) -> str:
    """
    Propose une recommandation intermédiaire générale (ex: repos, hydratation, surveillance).
    Règle stricte: Cette recommandation doit rester prudente et ne remplace pas l'avis du médecin.
    """
    return f"Action: Recommandation intermédiaire enregistrée -> {recommendation}"