def prompt_blocks(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur):
    return {
        # --- Blocs fixes (toujours inclus) ---
        "objectif": f"""
🎯 Objectif de la tâche
Génère un brief commercial clair et structuré pour préparer un rendez-vous entre un commercial TIBCO et un interlocuteur de {entreprise_nom}. 
Attention, {entreprise_nom} peut être une collectivité territoriale ou une entreprise, mais je la désignerai dans ce prompt comme une "entreprise" pour faciliter la compréhension. 
Le brief doit inclure une analyse de l’actualité de l’entreprise cliente, une synthèse de ses enjeux, une présentation des offres pertinentes de TIBCO et un plan d’action pour la suite des échanges.
Ne sois pas laudatif, n'utilise pas d'expressions génériques et essaie d'aller à l'essentiel.
""",

        "contexte_tibco": """
🏢 Contexte entreprise (TIBCO)
TIBCO, à ne surtout pas confondre avec l'entreprise américaine Tibco Software, est une ESN française spécialisée dans 5 domaines :

- Digital Workplace : prolongation de la durée de vie des équipements.  
- Réseaux : maintenance, continuité, résilience.  
- Cybersécurité : sécurisation des SI.  
- Cloud & On-Premise : solutions hybrides.  
- Data : valorisation et souveraineté numérique.  

Elle emploie 1700 collaborateurs sur 113 points de présence en France. 
En 2023, 50% de son chiffre d’affaires (150 M€) provenait d’activités écoresponsables.
""",

        "contexte_commercial": f"""
👤 Contexte commercial
Le commercial est en rendez-vous avec {collab_nom}, qui travaille pour l'entreprise {entreprise_nom}.

Voici les services proposés par Tibco qui ont été identifiés comme pouvant intéresser l'entreprise {entreprise_nom} : {liste_services}.

Voici le contexte de cet entretien : {contexte}
""",

        "structure_intro": """
📋 Structure attendue de la réponse
""",

        "structure_resume": """
🧩 Résumé de l'entreprise cliente et son actualité (≥ 2000 signes)  
Résumé centré sur la France. Focalise sur les enjeux liés aux métiers TIBCO.
""",

        "structure_objectif_rdv": """
✍️ Objectif du rendez-vous (≥ 1000 signes)  
Abstract des objectifs du commercial TIBCO.
""",

        # --- Blocs optionnels (activables via formulaire) ---
        "actualite": f"""
📰 Actualité de {entreprise_nom} :
{actu_client}

📰 Actualité du secteur de {entreprise_nom}, le {secteur} :  
{news_secteur}
""",

        "problematique": """
🎯 Problématiques, objectifs et attentes du client (≥ 1000 signes)  
Déduis-les à partir de l’appel d’offres, des enjeux sectoriels et de leurs priorités. 
Identifie les enjeux concrets (cybersécurité, complexité du sourcing, modernisation, etc.).
""",

        "reponse_tibco": f"""
🛡️ Que propose Tibco face à ces problématiques ? (≥ 3000 signes)  
Mets en parallèle les services TIBCO et les besoins/problèmes identifiés.  
Présente chaque offre TIBCO pertinente grâce au schéma Caractéristique - Avantage - Bénéfice.  

📦 Offres TIBCO à intégrer :  
{liste_services}
""",

        "questions": """
🕵️ Questions à poser durant le rendez-vous (500 signes)  
En prenant bien en compte l'actualité de l'entreprise et de son secteur, et enfin les services de TIBCO, propose une liste de questions ouvertes et pertinentes.
""",

        "next_steps": """
🗓️ Prochaines étapes / plan d’action (≥ 1000 signes)  
Synthèse, proposition de 2e RDV, envoi doc, aide au CCTP.
"""
    }

def prompt_custom(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur, selected_blocks):
    blocks = prompt_blocks(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur)

    # Blocs fixes toujours inclus
    fixed_blocks = ["objectif", "contexte_tibco", "contexte_commercial", "structure_intro", "structure_resume", "structure_objectif_rdv"]

    # Mapping des choix utilisateur → vrais blocs
    optional_mapping = {
        "actualite": "actualite",
        "problematique": "problematique",
        "reponse_tibco": "reponse_tibco",
        "questions": "questions",
        "next_steps": "next_steps"
    }

    # Construire la liste finale
    final_keys = fixed_blocks + [optional_mapping[key] for key in selected_blocks if key in optional_mapping]

    return "\n".join([blocks[key] for key in final_keys])
