from app.state import MedicalState
from langchain_core.messages import AIMessage

def physician_node(state: MedicalState) -> dict:
    traitement = state.get("physician_treatment")

    if not traitement:
        traitement = "Aucune consigne spécifique du médecin traitant."
        
    message = AIMessage(
        content=f"Revue du médecin (Human-in-the-Loop) complétée. Conduite à tenir : {traitement}", 
        name="PhysicianReview"
    )
    
    return {"messages": [message]}