# Système Multi-Agents Médical — Orientation Clinique Préliminaire

> ⚠️ **Avertissement** : Ce système est un exercice académique réalisé dans le cadre du module Systèmes Multi-Agents (Pr. Mohamed YOUSSFI). Il ne constitue **pas un dispositif médical** et **ne fournit aucun diagnostic définitif**. Il propose uniquement une orientation clinique préliminaire, une synthèse clinique et une recommandation intermédiaire, toujours soumises à validation par un médecin traitant. **Ce système ne remplace pas une consultation médicale.**

---

## 1. Présentation du projet

Ce projet implémente un workflow multi-agents avec **LangGraph** simulant le parcours d'orientation clinique d'un patient :

1. Le patient décrit ses symptômes initiaux.
2. Un agent de diagnostic pose 5 questions ciblées et s'appuie sur un protocole médical externe (via MCP) pour affiner ses questions.
3. Une recommandation intermédiaire prudente est générée.
4. Un médecin traitant intervient manuellement (Human-in-the-Loop) pour valider ou ajuster la conduite à tenir.
5. Un rapport final structuré est produit, accessible via API et frontend.

Le tout est orchestré par un agent **Supervisor**, exposé via une **API FastAPI**, et accessible via un **frontend Streamlit**.

---

## 2. Architecture du graphe LangGraph

```
START
  |
  v
Supervisor
  |
  v
DiagnosticAgent
  |
  +--> Tool: ask_patient (boucle jusqu'à 5 questions)
  |
  +--> Tool: fetch_mcp_protocol (consultation du serveur MCP)
  |
  +--> Tool: recommend_interim_care
  |
  v
Supervisor
  |
  v
PhysicianReview (Human-in-the-Loop)
  |
  v
Supervisor
  |
  v
ReportAgent
  |
  v
Supervisor
  |
  v
END
```

### Capture d'écran du graphe (LangGraph Studio)

<img width="636" height="447" alt="schema_graphe" src="https://github.com/user-attachments/assets/78b141ba-74ea-49f1-bb65-8fe0b39683f9" />


---

## 3. Agents

| Agent | Rôle |
|---|---|
| **Supervisor** | Orchestre le workflow et décide du nœud suivant en fonction de l'état (`next`). |
| **DiagnosticAgent** | Pose jusqu'à 5 questions au patient via le tool `ask_patient`, interroge le protocole MCP via `fetch_mcp_protocol`, puis déclenche `recommend_interim_care`. |
| **PhysicianReview** | Point d'interruption Human-in-the-Loop. Le médecin reçoit la synthèse et propose une conduite à tenir avant la suite du workflow. |
| **ReportAgent** | Génère le rapport final structuré (Markdown) à partir de l'historique de consultation et de la décision médicale. |

---

## 4. État partagé du graphe

```python
class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    question_count: int
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str
```

---

## 5. Intégration MCP

Un serveur MCP (`mcp_server/server.py`, basé sur **FastMCP**) expose un outil `get_standard_protocol(symptom)` qui retourne les directives médicales standards pour un symptôme donné (toux, fièvre, douleur thoracique, etc.).

Le backend communique avec ce serveur via le client `mcp_client.py` (`backend/app/tools/mcp_client.py`), en **transport stdio** : le serveur est lancé comme sous-processus par le backend, sans port réseau à gérer.

---

## 6. API FastAPI

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/sessions/start` | Initialise une nouvelle session (génère un `thread_id`). |
| `POST` | `/consultation/start` | Démarre la consultation avec les symptômes initiaux du patient. |
| `POST` | `/consultation/reply` | Envoie la réponse du patient à la question en cours. |
| `POST` | `/consultation/resume` | Reprend le workflow après la décision du médecin (Human-in-the-Loop). |
| `GET` | `/consultation/{thread_id}` | Retourne l'état courant de la consultation et l'historique. |
| `GET` | `/consultation/{thread_id}/report` | Retourne le rapport final structuré. |

Documentation interactive disponible sur `http://127.0.0.1:8000/docs` une fois le backend lancé.

---

## 7. Frontend (Streamlit)

Le frontend permet de suivre les 4 écrans minimums attendus :

| Écran | Description |
|---|---|
| **Écran 1** | Saisie du cas initial patient. |
| **Écran 2** | Questions/réponses successives avec le système (chat). |
| **Écran 3** | Espace médecin : revue de la synthèse et saisie de la conduite à tenir. |
| **Écran 4** | Affichage du rapport final structuré. |

<img width="1904" height="902" alt="image" src="https://github.com/user-attachments/assets/73fb0cad-7c1f-482e-bc2a-6e992a60bc7d" />
<img width="1898" height="903" alt="image" src="https://github.com/user-attachments/assets/01a2aae3-8cac-4895-ae6d-a082d48501cd" />
<img width="1913" height="907" alt="image" src="https://github.com/user-attachments/assets/7d5ce278-4019-4b91-9653-b6b03ee0db95" />
<img width="1906" height="907" alt="image" src="https://github.com/user-attachments/assets/cfa3f211-3961-4f73-98bf-c4abe1d16206" />
<img width="1909" height="839" alt="image" src="https://github.com/user-attachments/assets/20b1ca3b-38ef-4d0b-81ac-334edc05c723" />



---

## 8. Structure du projet

```
project/
├── backend/
│   ├── app/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   ├── tools/
│   │   │   ├── patient_tools.py
│   │   │   ├── care_tools.py
│   │   │   └── mcp_client.py
│   │   └── api.py
│   ├── langgraph.json
│   └── requirements.txt
├── mcp_server/
│   └── server.py
├── frontend/
│   └── app.py
└── README.md
```

---

## 9. Installation et exécution

### Prérequis
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installé
- Ollama (ou accès au modèle `gpt-oss:20b-cloud` configuré)

> Le serveur MCP fonctionne en transport **stdio** : il est lancé automatiquement comme sous-processus par le backend, aucune commande séparée n'est nécessaire pour le démarrer.

### 9.1 Backend FastAPI

```bash
cd backend
uv sync
uv run uvicorn app.api:app --reload --port 8000
```

L'API est accessible sur `http://127.0.0.1:8000`.

### 9.2 LangGraph Studio (test et debug du graphe)

```bash
cd backend
uv add langgraph-cli[inmem]
uv run langgraph dev
```

### 9.3 Frontend Streamlit

```bash
cd frontend
uv add streamlit requests
uv run streamlit run app.py
```

L'interface est accessible sur `http://localhost:8501`.

### 9.4 Ajouter une dépendance

```bash
uv add <nom-du-paquet>
```

`uv` met à jour automatiquement `pyproject.toml` et le lockfile.

---

## 10. Scénarios de test

| Cas | Description | Vérifications |
|---|---|---|
| **Cas 1** | Syndrome respiratoire simple (toux, fièvre) | 5 questions posées, protocole MCP consulté, recommandation intermédiaire générée, revue médecin, rapport final. |
| **Cas 2** | Cas avec red flags (douleur thoracique, difficulté à respirer) | Le protocole MCP doit signaler l'urgence ; vérifier la cohérence de la recommandation. |
| **Cas 3** | Cas bénin (rhume, fatigue légère) | Workflow complet jusqu'au rapport final, ton prudent respecté. |

---

## 11. Choix techniques

- **LangGraph** pour la modélisation du workflow multi-agents avec état partagé persistant via checkpointer.
- **Human-in-the-Loop natif** via `interrupt_before=["physician_review"]` et `interrupt_after=["patient_tools"]`, exploitant le mécanisme d'interruption/reprise de LangGraph.
- **MCP en transport stdio** plutôt que streamable-http, pour simplifier le déploiement local (pas de gestion de port/host, le serveur est démarré à la demande par le client).
- **FastAPI** pour exposer le graphe avec persistance de session via `thread_id`.
- **Streamlit** pour un frontend simple et rapide à itérer, suffisant pour couvrir les 4 écrans demandés.

---

## 12. Limites connues et axes d'amélioration

- Les champs `interim_care` et `diagnostic_summary` de l'état ne sont pas encore systématiquement renseignés de façon structurée (l'information transite actuellement via l'historique des messages).
- La phrase obligatoire de non-substitution à une consultation médicale est actuellement garantie par consigne au modèle dans le prompt du `ReportAgent` ; une vérification programmatique post-génération pourrait être ajoutée pour la garantir à 100 %.
- Pas encore de persistance en base de données (le checkpointer utilisé est en mémoire) ni d'export PDF du rapport (bonus non implémentés à ce stade).

---

## 13. Auteurs

Chamseddine Reyane

## 14. Encadrement

Projet réalisé dans le cadre du module Systèmes Multi-Agents — Pr. Mohamed YOUSSFI.
