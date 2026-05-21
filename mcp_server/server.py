from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MedicalGuidelines", host="0.0.0.0", port=23000)

@mcp.tool()
def get_standard_protocol(symptom: str) -> str:
    """
    Retourne les directives médicales et posologies standards pour un symptôme donné.
    """

    guidelines = {
        # --- CAS 1 : Syndrome respiratoire simple ---
        "toux": "Protocole Standard (Respiratoire) : Si toux sèche et invalidante, sirop antitussif. Éviter les irritants. Surveillance de la saturation.",
        "fievre": "Protocole Standard (Respiratoire) : Paracétamol 1g (maximum 4g par jour), prises espacées de 6h. Hydratation abondante.",
        
        # --- CAS 2 : Cas avec Red Flags (Urgences) ---
        "douleur thoracique": " Urgence : Suspicion de syndrome coronarien aigu. Orientation immédiate vers les urgences (SAMU 15). ECG en urgence.",
        "respirer": " Urgence : Détresse respiratoire aiguë. Oxygénothérapie immédiate. Transfert médicalisé urgent.",
        "sang": " Urgence : Hémoptysie (crachat de sang). Hospitalisation requise pour imagerie thoracique immédiate.",

        # --- CAS 3 : Cas bénin ---
        "rhume": "Protocole Bénin : Lavage nasal régulier au sérum physiologique. Repos. Pas d'antibiothérapie nécessaire.",
        "fatigue": "Protocole Bénin : Repos, hydratation, cure de vitamines. Si la fatigue persiste au-delà de 7 jours, programmer une prise de sang de contrôle.",
        "gorge": "Protocole Bénin : Pastilles adoucissantes, tisanes chaudes. Évolution généralement favorable en 3 à 5 jours."
    }
    
    symptom_lower = symptom.lower()

    for key, protocol in guidelines.items():
        if key in symptom_lower:
            return protocol
            
    return f"Aucun protocole standardisé trouvé dans la base MCP pour : {symptom}."

if __name__ == "__main__":
    print(" Lancement du serveur MCP Médical sur http://0.0.0.0:23000")
    mcp.run(transport="streamable-http")