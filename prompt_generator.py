def prompt_generator_func(entreprise_nom, collab_nom, centre_interet_inputs, contexte, secteur, actu_client, news_secteur, services_tibco, collab_fonction, autre) :
    prompt = f"""
    🎯 Objectif de la tâche
    Génère un brief commercial clair et structuré pour préparer un rendez-vous entre un commercial TIBCO et un interlocuteur de {entreprise_nom}. Le brief doit inclure une analyse de l’actualité de l’entreprise cliente, une synthèse de ses enjeux, une présentation des offres pertinentes de TIBCO et un plan d’action pour la suite des échanges.

    🏢 Contexte entreprise (TIBCO)
    TIBCO, à ne surtout pas confondre avec l'entreprise américaine Tibco Software, est une ESN française spécialisée dans 5 domaines :

    Digital Workplace : prolongation de la durée de vie des équipements.

    Réseaux : maintenance, continuité, résilience.

    Cybersécurité : sécurisation des SI.

    Cloud & On-Premise : solutions hybrides.

    Data : valorisation et souveraineté numérique.

    Elle emploie 1700 collaborateurs sur 113 points de présence en France. En 2023, 50% de son chiffre d’affaires (150 M€) provenait d’activités écoresponsables.

    👤 Contexte commercial
    Le commercial est en rendez-vous avec {collab_nom}, qui occupe la fonction de {collab_fonction} dans l'entreprise {entreprise_nom}.

    Parmi les services proposés par TIBCO, l'entreprise cliente s’intéresse à {centre_interet_inputs}.

    Voici le contexte de cet entretien : {contexte}

    📰 Actualité de {entreprise_nom} :

    {actu_client}

    📰 Actualité du secteur de {entreprise_nom}, le {secteur} :  

    {news_secteur}  

    📦 Offres TIBCO à intégrer
    Tu dois intégrer dans le brief des exemples concrets et détaillés à partir des descriptions suivantes (elles sont divisées par thème) :

    {services_tibco}

    📋 Structure attendue de la réponse
    🧩 Résumé de l'entreprise cliente et son actualité (≥ 2000 signes)
    Résumé centré sur la France. Focalise sur les enjeux liés aux métiers TIBCO.

    ✍️ Objectif du rendez-vous (≥ 1000 signes)
    Abstract des objectifs du commercial TIBCO.

    🧭 Résumé des offres TIBCO pertinentes (≥ 2000 signes)
    Utilise les exemples concrets fournis dans le bloc “Offres TIBCO à intégrer”.

    🎯 Problématiques, objectifs et attentes du client (≥ 1000 signes)
    Déduis-les à partir de l’appel d’offres, des enjeux sectoriels et de leurs priorités.Identifie les enjeux concrets (cybersécurité, complexité du sourcing, modernisation, etc.)

    🛡️ Réponses TIBCO aux problématiques (≥ 2000 signes)
    Mets en parallèle les sous-offres TIBCO et les besoins/problèmes identifiés.
    Présente chaque offre TIBCO pertinente grâce au schéma Caractéristique - Avantage - Bénéfice. 
    Caractéristique : Ce qu’est le produit ou service (aspect technique, fonction).
    Avantage : Ce que fait cette caractéristique (l’utilité concrète).
    Bénéfice : Ce que cela apporte au client (ce qu’il y gagne, émotionnellement ou en résultats).


    🕵️ Questions à poser durant le rendez-vous (500 signes)
    En prenant bien en compte la fonction de l'interlocuteur, {collab_fonction}, propose une liste de questions ouvertes et pertinentes. 
    
    ❓{autre}
    Réponds à la question : {autre} 

    🗓️ Prochaines étapes / plan d’action (≥ 1000 signes)
    Synthèse, proposition de 2e RDV, envoi doc, aide au CCTP.
    """

    return prompt