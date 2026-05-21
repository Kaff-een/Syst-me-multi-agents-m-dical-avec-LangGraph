import sys
from langchain_core.tools import tool

@tool
def fetch_mcp_protocol(symptom: str) -> str:
    """
    Interroge le serveur MCP externe pour récupérer le protocole médical standard d'un symptôme.
    """
    return f"Action (Via Serveur MCP) : Recherche du protocole pour '{symptom}' demandée."