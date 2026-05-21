from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.graph import api_graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="API d'Orientation Clinique Préliminaire")

class PatientInput(BaseModel):
    symptomes: str

class PhysicianInput(BaseModel):
    traitement: str

class ConsultationId(BaseModel):
    thread_id: str

@app.post("/sessions/start")
def start_session():
    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id, "message": "Nouvelle session initialisée."}

@app.post("/consultation/start")
def start_consultation(thread_id: str, payload: PatientInput):
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {"messages": [HumanMessage(content=payload.symptomes, name="Patient")]}

    result = api_graph.invoke(initial_state, config)
    
    return {"status": "consultation_en_cours", "dernier_etat": f"Vérifiez /consultation/{thread_id}"}

@app.post("/consultation/resume")
def resume_consultation(thread_id: str, payload: PhysicianInput):
    config = {"configurable": {"thread_id": thread_id}}
    state = api_graph.get_state(config)

    if not state or "physician_review" not in state.next:
        raise HTTPException(status_code=400, detail="La consultation n'est pas en attente du médecin.")
 
    api_graph.update_state(config, {"physician_treatment": payload.traitement})

    api_graph.invoke(None, config)
    
    return {"status": "reprise_effectuee", "message": "Traitement enregistré, rapport en cours de génération."}

@app.get("/consultation/{thread_id}")
def get_consultation_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = api_graph.get_state(config)
    
    if not state.values:
        raise HTTPException(status_code=404, detail="Consultation introuvable.")

    historique_propre = []
    
    for m in state.values.get("messages", []):
        if m.type == "human" or getattr(m, "name", "") == "Patient":
            historique_propre.append({"role": "Patient", "content": m.content})

        elif getattr(m, "name", "") == "ask_patient" and m.content:
            question = m.content
   
            if "->" in question:
                question = question.split("->")[-1].strip()
            historique_propre.append({"role": "Assistant", "content": question})

        elif m.type == "ai" and m.content:
            historique_propre.append({"role": "Assistant", "content": m.content})


    return {
        "en_attente_de": state.next,
        "historique": historique_propre,
        "questions_posees": state.values.get("question_count", 0)
    }

@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = api_graph.get_state(config)
    
    messages = state.values.get("messages", [])

    for msg in reversed(messages):
        if msg.name == "ReportAgent":
            return {"report": msg.content}
            
    return {"message": "Le rapport n'est pas encore généré ou la consultation est inachevée."}


class PatientReply(BaseModel):
    reponse: str

@app.post("/consultation/reply")
def reply_to_question(thread_id: str, payload: PatientReply):
    config = {"configurable": {"thread_id": thread_id}}

    api_graph.update_state(config, {"messages": [HumanMessage(content=payload.reponse, name="Patient")]})

    api_graph.invoke(None, config)
    
    return {"status": "reponse_enregistree"}