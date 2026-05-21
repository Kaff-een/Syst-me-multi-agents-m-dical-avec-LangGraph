from langchain_core.tools import tool

@tool
def ask_patient(question: str) -> str:
    """
    Pose une question médicale ciblée au patient pour affiner l'orientation.
    À utiliser strictement pour poser la prochaine question.
    """
    # L'outil enregistre la question. L'interruption (Human-in-the-loop) 
    # pour récupérer la réponse sera gérée plus tard par le graphe.
    return f"Action: Question envoyée au patient -> {question}"