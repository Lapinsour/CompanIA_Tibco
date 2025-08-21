def prompt_generator_func(entreprise_nom, collab_nom, liste_services, centre_interet_inputs, contexte, secteur, actu_client, news_secteur, services_tibco, collab_fonction, autre) :
    prompt = f"""
    🎯 Objectif de la tâche
    Génère un brief commercial clair et structuré pour préparer un rendez-vous entre un commercial TIBCO et un interlocuteur de {entreprise_nom}. Attention, {entreprise_nom} peut être une collectivité territoriale ou une entreprise, mais je la désignerai dans ce prompt comme une "entreprise" pour faciliter la compréhension. Le brief doit inclure une analyse de l’actualité de l’entreprise cliente, une synthèse de ses enjeux, une présentation des offres pertinentes de TIBCO et un plan d’action pour la suite des échanges.
    Ne sois pas laudatif, n'utilise pas d'expressions génériques et essaie d'aller à l'essentiel.
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

    Voici les services proposés par Tibco qui ont été identifiés comme pouvant intéresser l'entreprise {entreprise_nom} : {liste_services}.
    

    Voici le contexte de cet entretien : {contexte}

    📰 Actualité de {entreprise_nom} :

    {actu_client}

    📰 Actualité du secteur de {entreprise_nom}, le {secteur} :  

    {news_secteur}  

    📦 Offres TIBCO à intégrer
    Tu dois intégrer dans le brief des exemples concrets et détaillés à partir des descriptions suivantes (elles sont divisées par thème) :

    {liste_services}

    📋 Structure attendue de la réponse
    🧩 Résumé de l'entreprise cliente et son actualité (≥ 2000 signes)
    Résumé centré sur la France. Focalise sur les enjeux liés aux métiers TIBCO.

    ✍️ Objectif du rendez-vous (≥ 1000 signes)
    Abstract des objectifs du commercial TIBCO.

    🎯 Problématiques, objectifs et attentes du client (≥ 1000 signes)
    Déduis-les à partir de l’appel d’offres, des enjeux sectoriels et de leurs priorités.Identifie les enjeux concrets (cybersécurité, complexité du sourcing, modernisation, etc.)

    🛡️ Réponses TIBCO aux problématiques (≥ 3000 signes)
    Mets en parallèle les services TIBCO et les besoins/problèmes identifiés.
    Présente chaque offre TIBCO pertinente grâce au schéma Caractéristique - Avantage - Bénéfice. N'hésite pas à détailler / donner des exemples tirés de la liste de services Tibco.
    Caractéristique : Ce qu’est le produit ou service (aspect technique, fonction).
    Avantage : Ce que fait cette caractéristique (l’utilité concrète).
    Bénéfice : Ce que cela apporte au client (ce qu’il y gagne, émotionnellement ou en résultats).


    🕵️ Questions à poser durant le rendez-vous (500 signes)
    En prenant bien en compte la fonction de l'interlocuteur, {collab_fonction}, mais également l'actualité de l'entreprise et de son secteur, et enfin les services de tibco, propose une liste de questions ouvertes et pertinentes. 
    
    ❓ Autre question (1000 signes) : {autre}
    Réponds à la question : {autre} en prenant en compte toutes les informations à ta disposition, l'actualité de l'entreprise et de son secteur, et enfin les services de tibco.

    🗓️ Prochaines étapes / plan d’action (≥ 1000 signes)
    Synthèse, proposition de 2e RDV, envoi doc, aide au CCTP.
    """

    return prompt