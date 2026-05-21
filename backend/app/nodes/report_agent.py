from app.state import MedicalState
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

llm = ChatOllama(model="gpt-oss:20b-cloud", temperature=0)

def report_node(state: MedicalState) -> dict:
    messages = state.get("messages", [])
    physician_treatment = state.get("physician_treatment", "Aucun traitement spécifique renseigné par le médecin.")

    conversation = ""
    for m in messages:
        if getattr(m, "name", "") not in ["fetch_mcp_protocol", "recommend_interim_care"] and m.content:
            role = "Patient" if m.type == "human" or getattr(m, "name", "") == "Patient" else "Agent"
            content = m.content.split("->")[-1].strip() if "->" in m.content else m.content
            conversation += f"{role} : {content}\n"

    prompt = (
        "Tu es l'Agent de Reporting (Report Agent). Ton rôle exclusif est de générer un rapport médical structuré "
        "basé sur la consultation qui vient de se terminer.\n\n"
        f"Voici l'historique de l'interrogatoire :\n{conversation}\n\n"
        f"Voici la décision et le traitement prescrits par le médecin traitant :\n{physician_treatment}\n\n"
        "Rédige un rapport final professionnel avec les sections suivantes (utilise le format Markdown) :\n"
        "### 1. Motif initial et Symptômes\n"
        "### 2. Synthèse de l'interrogatoire\n"
        "### 3. Recommandations et Avis Médical\n\n"
        "IMPORTANT : Tu dois obligatoirement inclure cette phrase exacte à la toute fin du rapport :\n"
        "**'Ce système ne remplace pas une consultation médicale.'**"
    )

    system_message = SystemMessage(content=prompt)
    response = llm.invoke([system_message])
    response.name = "ReportAgent"


    return {
        "messages": [response],
        "final_report": response.content
    }