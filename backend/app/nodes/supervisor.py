from app.state import MedicalState

def supervisor_node(state: MedicalState) -> dict:
    messages = state.get("messages", [])
    question_count = state.get("question_count", 0)
    print("\n" + "="*30)
    print("DEBUG SUPERVISOR")
    if messages:
        dernier_msg = messages[-1]
        nom_expediteur = getattr(dernier_msg, "name", "AUCUN NOM (C'est peut-être le problème !)")
        type_msg = type(dernier_msg).__name__
        print(f"Expéditeur : {nom_expediteur}")
        print(f"Type de message : {type_msg}")
        if hasattr(dernier_msg, "tool_calls") and dernier_msg.tool_calls:
            print(f"Outils demandés : {dernier_msg.tool_calls}")
    print(f"Compteur de questions : {question_count}")
    print("="*30 + "\n")
    if not messages or len(messages) <= 1:
        return {"next": "diagnostic_agent"}
        
    last_sender = messages[-1].name

    if last_sender == "DiagnosticAgent":
        if question_count >= 5:
            return {"next": "physician_review"}
        else:
            return {"next": "diagnostic_agent"}
    elif last_sender == "PhysicianReview":
        return {"next": "report_agent"}
 
    elif last_sender == "ReportAgent":
        return {"next": "FINISH"}
        
    return {"next": "diagnostic_agent"}