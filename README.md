#COMPANIA
CompanIA est une application qui : 
- génère un prompt à partir des entrées d'un formulaire et enrichi par du RAG basé : 
        - sur des informations sur les offres de services Tibco stockées dans une BDD vectorielle Tibco
        - sur les actualités de l'entreprise qui fait l'objet de l'entretien et de son secteur récupérées via webscraping et l'API NewsAPI, 
- requête ce prompt à l'api OpenAI afin de générer un brief de préparation d'entretien commercial, 
- puis envoie la réponse du LLM ainsi que des informations récupérées sur les BDD Tibco sous forme de mail au(x) destinataire(s) sélectionné(s), 
- en ajoutant en pièce jointe un fichier résumant les contrats dont dispose Tibco avec l'entreprise qui fait l'objet de l'entretien ainsi qu'une version text-to-speech du brief.

CompanIA est destinée à la cinquantaine de commerciaux Tibco. L'accès au formulaire leur est conférée par la SI, via le groupe de sécurité Azure des commerciaux. 

Elle est déployée sur srv-scripts-to. 


Version: 0.2 (25-06-2025) 

Ce fichier README a été généré le 25-06-2025 par Pierre GARRIGUES.

Dernière mise-à-jour le : 25-06-2025.

##Fichiers de l'application

📦 V0.2.0
├── 📁 static/              
│   └── 📄 logo.png           
├── 📁 templates/               
│   └── 📄 formulaire.html                --Formulaire CompanIA
│   └── 📄 suivi_form.html                --Formulaire de suivi (notation)
│   └── 📄 suivi_confirmation.html        --Formulaire de confirmation de note
├── 📁 modules/               
│   └── 📄 __init__.py                    --Fichier vide pour accéder au contenu du dossier Modules depuis script.py
│   └── 📄 liste_clients_tibco.py         --Requête sur Table CLIENTS pour proposer les clients Tibco existant dans le formulaire
│   └── 📄 liste_id_rapport_suivi.py      --Requête sur Table RAPPORTS_COMPANIA pour proposer les ident de rapport existant dans le formulaire de suivi
│   └── 📄 logging_config.py              --Fichier de configuration du log
│   └── 📄 prompt_generator.py            --Génération du prompt à partir des éléments du RAG et du formulaire. LE PROMPT EST MODIFIABLE EN DUR DANS CE FICHIER.
│   └── 📄 rag_actu_officielle.py         --Connexion aux API Pappers & BOAMP pour récupérer des informations officielles sur l'entreprise.
│   └── 📄 rag_newsapi.py                 --Connexion à l'API NewsAPI pour récupérer des actualités sur l'entreprise.
│   └── 📄 rag_secteur.py                 --Webscraping pour récupérer l'actualité du secteur et la faire résumer par ChatGPT.
│   └── 📄 rag_sql_tibco.py               --Requête sur HA-DWH pour récupérer les contrats existants entre l'entreprise et Tibco.
│   └── 📄 sauvegarde_rapport_sql.py      --Insère les infos du rapport généré dans la table RAPPORTS_COMPANIA.
│   └── 📄 send_mail.py                   --Met en forme la réponse de ChatGPT pour envoyer un mail & générer un text-to-speech. Envoie le mail. 
├── 📁 logs/
│   └── 📄 log_maj.txt                    --Log des modifications pour chaque màj
│   └── 📄 errors.txt                     --Log des erreurs
│   └── 📄 api.log                        --Log des utilisations de l'application                
├── 📄 .env
├── 📄 requirements.txt
├── 📄 api.py                             --Lance l'appli CompanIA. Appelle script.py.
├── 📄 script.py                          --Coordonne l'application. Effectue le webscraping sur l'actualité de l'entreprise.
├── 📄 connect_sql_suivi.py               --Envoie les notes de suivi vers la table SUIVI_UTILISATEUR_COMPANIA.
├── 📄 actualisation_actu_pinecone_script.py  
├── 📄 Run-CompanIA.bat                
└── 📄 README.md

-- NOTE : actualisation_actu_pinecone_script.py ne fait pas directement partie de l'application. Il est exécuté chaque semaine. Il purge la BDD vectorielle Pinecone des vieilles actus des entreprises et rafraîchit ces actualités en lançant un webscraping pour chaque entreprise présente dans la BDD Pinecone (celles qui ont déjà fait l'objet de rapports.)
