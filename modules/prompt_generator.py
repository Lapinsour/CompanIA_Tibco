def prompt_generator_func(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur) :
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
    Le commercial est en rendez-vous avec {collab_nom}, qui travaille dans l'entreprise {entreprise_nom}.

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
    Ce résumé doit être un texte en un ou deux paragraphes. 
    Résumé centré sur la France. Focalise sur les enjeux liés aux métiers TIBCO.    

    🎯 Problématiques, objectifs et attentes du client (≥ 1000 signes)
    Déduis-les à partir de l’appel d’offres, des enjeux sectoriels et de leurs priorités.Identifie les enjeux concrets (cybersécurité, complexité du sourcing, modernisation, etc.)
   
    🕵️ Questions à poser durant le rendez-vous (500 signes)
    En prenant bien en compte l'actualité de l'entreprise et de son secteur, et  les services de tibco, propose une liste de questions ouvertes et pertinentes.     

    🗓️ Prochaines étapes / plan d’action (≥ 1000 signes)
    Sélections de services et offres Tibco pouvant être proposés à l'entreprise démarchée (en une ou deux lignes, pas plus), Synthèse, proposition de 2e RDV, envoi doc, aide au CCTP.
    """

    return prompt