import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Orientation Clinique", layout="centered")
st.title(" Système medicale")
st.caption("Ce système ne remplace pas une consultation médicale.")


if "thread_id" not in st.session_state: 
    st.session_state.thread_id = None
if "etat_consultation" not in st.session_state:
    st.session_state.etat_consultation = "accueil"

if not st.session_state.thread_id:
    st.subheader("Écran 1 : Nouveau cas")
    symptomes = st.text_area("Décrivez vos symptômes initiaux :")
    
    if st.button("Démarrer la consultation"):
        res = requests.post(f"{API_URL}/sessions/start").json()
        st.session_state.thread_id = res["thread_id"]
        st.session_state.etat_consultation = "en_cours"
        requests.post(f"{API_URL}/consultation/start?thread_id={st.session_state.thread_id}", json={"symptomes": symptomes})
        st.rerun()

else:
    state_res = requests.get(f"{API_URL}/consultation/{st.session_state.thread_id}").json()
    en_attente_de = state_res.get("en_attente_de")

    st.divider()
    for msg in state_res.get("historique", []):
        if not msg.get("content"): 
            continue
            
        role = "user" if msg["role"] in ["Patient", "PhysicianReview"] else "assistant"
        with st.chat_message(role):
            st.markdown(f"**{msg['role']}**: {msg['content']}")
            
    st.divider()

    if en_attente_de and "diagnostic_agent" in en_attente_de:
        st.subheader("Écran 2 : Question du système")
        reponse = st.chat_input("Votre réponse...")
        if reponse:
            requests.post(f"{API_URL}/consultation/reply?thread_id={st.session_state.thread_id}", json={"reponse": reponse})
            st.rerun()

    elif en_attente_de and "physician_review" in en_attente_de:
        st.subheader("Écran 3 : Espace Médecin (Human-in-the-Loop)")
        st.warning("Le système a terminé son analyse préliminaire. En attente de la validation médicale.")
        traitement = st.text_area("Conduite à tenir ou traitement prescrit :")
        if st.button("Valider l'intervention médicale"):
            requests.post(f"{API_URL}/consultation/resume?thread_id={st.session_state.thread_id}", json={"traitement": traitement})
            st.rerun()
 
    elif st.session_state.etat_consultation == "report_agent" or st.session_state.etat_consultation == "FINISH":
        st.header("Écran 4 : Rapport Final")

        report_res = requests.get(f"{API_URL}/consultation/{st.session_state.thread_id}/report")
    
        if report_res.status_code == 200:
            data = report_res.json()
            rapport = data.get("report", "Erreur lors de la récupération du rapport.")

            st.markdown(rapport)
        
            st.success("Consultation clôturée.")