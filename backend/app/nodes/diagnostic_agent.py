from app.state import MedicalState
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from app.tools.patient_tools import ask_patient
from app.tools.care_tools import recommend_interim_care
from app.tools.mcp_client import fetch_mcp_protocol
from langchain_ollama import ChatOllama

llm = ChatOllama(model="gpt-oss:20b-cloud", temperature=0)

def diagnostic_node(state: MedicalState) -> dict:
    messages = state.get("messages", [])
    question_count = state.get("question_count", 0)
    
    a_fait_reco = any(getattr(m, "name", "") == "recommend_interim_care" for m in messages)

    dernier_msg = messages[-1] if messages else None
    vient_de_lire_mcp = getattr(dernier_msg, "name", "") == "fetch_mcp_protocol"
    
    if question_count >= 5:
        if a_fait_reco:
            llm_with_tools = llm 
        else:
            llm_with_tools = llm.bind_tools([recommend_interim_care], tool_choice="recommend_interim_care")
    else:
        if vient_de_lire_mcp:
            llm_with_tools = llm.bind_tools([ask_patient], tool_choice="ask_patient")
        else:
            llm_with_tools = llm.bind_tools([ask_patient, fetch_mcp_protocol])
            
    instructions = (
        "Tu es un assistant d'orientation clinique préliminaire.\n"
        "Le système ne remplace pas une consultation médicale.\n"
        f"Tu as posé {question_count} question(s) sur 5.\n\n"
        "RÈGLES DE SURVIE ABSOLUES :\n"
        "1. Tu n'as PAS LE DROIT de générer du texte normal. Tu DOIS utiliser un outil technique.\n"
        "2. Pose UNE SEULE question à la fois. Tu ne dois appeler l'outil 'ask_patient' qu'UNE SEULE FOIS par tour, puis tu dois te taire et attendre la réponse du patient.\n"
        "3. Si le patient indique un symptôme (fièvre, toux), tu peux utiliser 'fetch_mcp_protocol' pour t'informer avant de poser ta question.\n"
        "4. Dès que le compteur atteint 5 questions, utilise IMPÉRATIVEMENT 'recommend_interim_care'."
    )
    
    system_message = SystemMessage(content=instructions)
    response = llm_with_tools.invoke([system_message] + messages)

    if hasattr(response, "tool_calls") and len(response.tool_calls) > 1:
        response.tool_calls = [response.tool_calls[0]]
        
    response.name = "DiagnosticAgent"
    
    nouveau_compte = question_count
    if hasattr(response, "tool_calls") and response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "ask_patient":
                nouveau_compte += 1
                
    return {
        "messages": [response],
        "question_count": nouveau_compte
    }