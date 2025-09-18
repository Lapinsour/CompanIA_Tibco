from pinecone import Pinecone
import pinecone
import hashlib
import re
import string
import random
import pyodbc
import unicodedata
import unstructured
from openai import OpenAI
import time
import os
import numpy
import html
import sys
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import datetime as dt
import feedparser
from transformers import AutoTokenizer
import json
from bs4 import BeautifulSoup
from newspaper import Article
from dateutil.relativedelta import relativedelta
from dateutil import parser
import random
import time
import asyncio
from dotenv import load_dotenv

#fonctions maison
from modules.send_mail import send_mail_func
from modules.sauvegarde_rapport_sql import sauvegarde_rapport_func
from modules.rag_sql_tibco import rag_sql_tibco
from modules.rag_sql_tibco import liste_client_rag
from modules.rag_secteur import rag_secteur_func
from modules.prompt_generator import prompt_generator_func
from modules.rag_actu_officielle import get_pappers_info, get_boamp_info
from modules.logging_config import logger
from modules.rag_newsapi import rag_newsapi
from modules.rag_wikipedia import wikipedia_resume
from modules.recommandations_services import recommandations_services
from modules.prompt_blocks import prompt_custom
from modules.scrapping_utils import google_news_scrap


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PAPPERS_API_KEY = os.getenv("PAPPERS_API_KEY")

entreprise_nom = sys.argv[1]
secteur = sys.argv[2] 
contexte = sys.argv[3]
collab_nom = sys.argv[4]
destinataire = sys.argv[5]
code_postal = sys.argv[6] 
self_prompt_yn = sys.argv[7]
self_prompt = sys.argv[8]

# Convertir la liste des destinataires en liste python
destinataires = destinataire.split(";")
destinataire_str = ", ".join(destinataires)

# Modèle : important pour les embeddings. Ne pas y toucher sinon on ne pourra plus interpréter la BDD Pinecone
model_name = "multilingual-e5-large"
dimension_model = 1024
max_tokens = 96
tokenizer = AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")

# Ce prompt sert à scanner la BDD vectorielle Pinecone via similarité sémantique. On peut le modifier.
# Dans Pinecone sont stockées toutes les actualités récentes de l'entreprise. 
# Ce prompt précise à ChatGPT lesquelles retourner. 
prompt_de_recherche_CLIENT = f"Quelle(s) actualité(s) pourraient influencer l'activité et le profit de l'entreprise {entreprise_nom}?"

# Crée une URL LinkedIn du contact rencontré dans l'entreprise
linkedin_url = f"https://www.google.com/search?q={collab_nom.replace(' ', '+')}+{entreprise_nom}+site:linkedin.com"
 




def Query_GPT(entreprise_nom, OPENAI_API_KEY,PINECONE_INDEX_NAME):
    '''
    Fonction principale
    Récupère les offres de service Tibco stockées dans Pinecone pertinentes
    Les formate pour les rendre intelligibles

    '''
    pc = Pinecone(
      api_key=PINECONE_API_KEY
    )
    # Connexion à l'index Pinecone
    index_pc = pc.Index(PINECONE_INDEX_NAME)  
    all_results_TIBCO = []

    # Pour chaque "centre d'intérêt" sélectionné par l'utilisateurice, on récupère toutes les offres de service Tibco listées dans Pinecone.
    #IMPORTANT : ici on n'utilise pas du tout de similarité sémantique.

             
    results_TIBCO = index_pc.query(
        namespace="DOC-TIBCO",
        vector=[0.0] * 1024,
        top_k=100, 
        include_values=False,
        include_metadata=True
    )
    all_results_interet = [result["metadata"]["text"] for result in results_TIBCO["matches"]]        
    all_results_TIBCO.append(all_results_interet)

    relevant_texts_TIBCO = all_results_TIBCO

    def format_tibco_services(nested_text_blocks): # Permet de formater les textes stockés dans Pinecone pour les rendre intelligibles par ChatGPT
        formatted_text = ""

        for sublist in nested_text_blocks:
            for block in sublist:  # on boucle dans chaque sous-liste
                services = re.split(r"(Service proposé par TIBCO\s*:\s*[^\s]+)", block)
                grouped = list(zip(services[1::2], services[2::2]))

                for title, content in grouped:
                    title_clean = title.strip()
                    content_clean = content.strip()
                    # "__" devient un point + espace (fin de phrase)
                    content_clean = re.sub(r'__+', '. ', content_clean)
                    # "_" devient un espace
                    content_clean = re.sub(r'_+', ' ', content_clean)
                    # Majuscule après un point
                    content_clean = re.sub(r'(?<=\.)\s+([a-z])', lambda m: ' ' + m.group(1).upper(), content_clean)
                    formatted_text += f"{title_clean}\n{content_clean}\n\n"

        return formatted_text.strip()
    services_tibco = format_tibco_services(relevant_texts_TIBCO)   
        
    
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        )

    # Fonction pour interroger ChatGPT
    def chat_gpt_actu(prompt_actu):
        '''
        # Requête à ChatGPT pour condenser l'actualité de l'entreprise en un résumé intelligible.
        # Ce résumé est ensuite intégré au rapport final, et envoyé avec le prompt à ChatGPT lors de l'édition du rapport.
        # Découper les étapes permet à ChatGPT de mieux se concentrer sur chaque tâche et d'obtenir de meilleurs résultats.
        
        '''
        system_content = f"Voici une sélection d'articles. A partir de cette sélection, résume en 1500 à 2500 signes l'actualité de l'entreprise {entreprise_nom}. Concentre-toi principalement sur l'actualité économique et sur l'actualité technologique.\
            N'INVENTE PAS. Ne sois pas laudatif, n'utilise pas d'expressions génériques et essaie d'aller à l'essentiel."
        response = client.chat.completions.create(        
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt_actu}
                ],
            temperature = 0 # Important : laisser la température à 0 pour éviter l'improvisation
        )
        return response.choices[0].message.content.strip()



    def rag_actu_client(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom):
        '''
        Récupère l'actu client par scraping ou récupération depuis Pinecone
        Appelle l'api NewsAPI pour trouver des actualités complémentaires
        Récupère l'actualité du secteur
        Ajoute le tout à un prompt, requête ChatGPT et renvoie un résumé des actualités de l'entreprise et de son secteur.
        '''
        news_client = google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME, model_name, entreprise_nom, secteur)

        actu_newsapi = rag_newsapi(entreprise_nom)
        prompt_actu = f"Voici une sélection d'articles sur l'entreprise {entreprise_nom}."  

        if news_client or actu_newsapi :
            if news_client :      
                for article in news_client:
                    prompt_actu+= str(article)
                

            if actu_newsapi:
                for article in actu_newsapi:
                    prompt_actu+= str(article['title']) 
                    prompt_actu+= str(article['description'])                         
            
            print("PROMPT", prompt_actu)
            response_text_actu_client = chat_gpt_actu(prompt_actu) # Renvoie un résumé de l'actualité de l'entreprise  
            print("REPONSE", response_text_actu_client)   
         
        else :
            response_text_actu_client = "Désolé, je n'ai pas trouvé d'actualité pour cette entreprise."            
        return response_text_actu_client

    news_secteur = rag_secteur_func(secteur)  
    actu_client = rag_actu_client(PINECONE_API_KEY, PINECONE_INDEX_NAME, entreprise_nom)  
    print(actu_client)
    
    
    #Cette étape permet de renvoyer l'en-tête du rapport généré par mail, qui concerne la relation entre Tibco et l'entreprise.
    #Elle prend en charge l'erreur qu'on reçoit quand on fait tourner l'application alors que TIBCOVIEW_TS n'est pas accessible.    
    relation_sql = None
    siret = None 
    
    try:
        liste_client = liste_client_rag()

        if entreprise_nom in liste_client :
            
            try:
                relation_sql, nb_aff,nb_aff_en_cours,total_budget, total_facture, siret, type_date, derniere_date = rag_sql_tibco(entreprise_nom)  
                  
                total_budget = f"{total_budget:,.2f}".replace(",", " ").replace(".", ",")
                total_facture = f"{total_facture:,.2f}".replace(",", " ").replace(".", ",")            
                if nb_aff != 0 : 
                    if type_date == "fin" :
                        reponse_relation_sql = f"Cette entreprise est déjà cliente de Tibco ! Plus précisément, nous avons {nb_aff} affaires terminées avec elle, pour un budget total de {total_budget}€ et une facturation totale de {total_facture}€.\n\
                        L'affaire la plus récente s'est terminée le {derniere_date}.\n\
                        Pour en savoir plus, vous trouverez en pièce jointe un tableau récapitulatif de la relation de Tibco et de l'entreprise {entreprise_nom}."
                    
                    if type_date == "création":                                           
                        reponse_relation_sql = f"Cette entreprise est déjà cliente de Tibco ! Plus précisément, nous avons {nb_aff} affaires avec elle, dont {nb_aff_en_cours} en cours, pour un budget total de {total_budget}€ et une facturation totale de {total_facture}€.\n\
                        L'affaire la plus récente a débuté le {derniere_date}.\n\
                        Pour en savoir plus, vous trouverez en pièce jointe un tableau récapitulatif de la relation de Tibco et de l'entreprise {entreprise_nom}."
                else : 
                    reponse_relation_sql = f"L'entreprise {entreprise_nom} est déjà cliente de Tibco, mais nous n'avons aucune affaire passée ou en cours avec elle."
            except pyodbc.Error as e :
                print(pyodbc.Error)
                reponse_relation_sql ="Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
            except Exception as e:
                print("Exception",e)
                reponse_relation_sql ="Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
    
        else :
            reponse_relation_sql ="Cette entreprise ne compte pas parmi les clients de Tibco... Pour l'instant !\nSi vous pensez qu'il s'agit d'une erreur, n'hésitez pas à nous la faire remonter."
            
    except pyodbc.Error as e :
        reponse_relation_sql ="ERREUR PYODBC : Aïe, nous n'avons pas pu remonter les informations quant à la relation de Tibco avec cette entreprise, car les serveurs de Tibco sont indisponibles entre 12h15 et 13h."
    


    wikipedia_text = wikipedia_resume(entreprise_nom)
    resume_inputs = f"Voici les informations que vous m'avez fournies : \n\
    Nom et secteur de l'entreprise : {entreprise_nom}, secteur {secteur}\n\
    Identité de votre contact : {collab_nom}\n\
    Contexte de l'entretien : {contexte}\n\
    Destinataire(s) du brief : {destinataire_str}"
    resume_inputs = resume_inputs.replace('\n', '<br>')


    all_results_services_TIBCO = index_pc.query(
        namespace="DOC-TIBCO",
        vector=[0.0] * 1024,
        top_k=1000,  # Tu peux augmenter si besoin
        include_values=False,
        include_metadata=True
    )

    all_services_TIBCO = [result["metadata"]["text"] for result in all_results_services_TIBCO["matches"]]

    

    # Recommandation de services susceptibles d'intéresser l'entreprise 
    '''
    Cette fonction renvoie une liste de services Tibco de la forme : 
    LS = ['Service proposé par TIBCO : Cyberdéfense Comment TIBCO peut Sensibiliser__conseiller : Sensibiliser__conseiller_Soyez_le_premier_rempart_de_votre_cyberdéfense_Sensibiliser_les_utilisateurs_Vos_utilisateurs_bénéficient_dun_programme_de_sensibilisation_personnalisé_via_notre_plateforme_de-learning_Évaluer_la_maturité_des_utilisateurs_Basés_sur_des_cas_dusages_vos_utilisateurs_apprennent_les_bons_réflexes_à_travers_des_campagnes_de_phishing_par_email_ou_SMSDes_quizz_pédagogiques_vous_permettent_dévaluer_et_daméliorer_les_cybers_bonnes_pratiques_Entraîner_les_décideurs_Entrainez_votre_Comité_de_direction_et_lensemble_des_services_Supports_à_gérer_une_situation_de_crise_en_cybersécurité', 'Service proposé par TIBCO : Cyberdéfense Comment TIBCO peut Évaluer_mon_Système_dInformation : Évaluer_mon_Système_dInformation_Point_de_départ_de_votre_stratégie_de_cyberdéfense_Analyser_la_valeur_de_votre_patrimoine_informatique_Tout_en_tenant_compte_de_votre_contexte_métier_et_de_vos_contraintes_opérationnelles_nous_réalisons_une_analyse_de_risques_pour_créer_votre_feuille_de_route_cybersécurité_et_protéger_votre_patrimoine_informationnel_Auditer_votre_infrastructure_Pour_mesurer_la_maturité_de_la_sécurité_de_votre_SI_nous_réalisons_un_audit_de_chacun_des_10_socles_techniques_suivants_Active_DirectoryConsole_antiviraleLocaux_informatiquesMessagerieMises_à_jour_OSPare-feuPostes_de_travailRéseauServeursSystème_de_sauvegarde_À_lissue_de_cet_audit_vous_disposerez_dune_feuille_de_route_priorisée_au_regard_des_différents_risques_identifiés_Réaliser_des_tests_dintrusions_Pour_mesurer_le_niveau_de_sécurité_de_votre_SI_nous_réalisons_un_test_dintrusion_qui_sappuie_sur_des_scénarios_dattaques_informatiques_identiques_à_celles_dun_hacker', 'Service proposé par TIBCO : Système Comment TIBCO peut Exploiter_lensemble_de_mes_systèmes : Exploiter_lensemble_de_mes_systèmes_Superviser_et_AdministrerInfogérer_votre_SI_auprès_de_Tibco_cest_vous_permettre_de_recentrer_vos_ressources_IT_sur_votre_informatique_métier_Analyser__auditer_Les_résultats_de_laudit_élargi_de_votre_infrastructure_autour_des_logiciels_matériels_et_les_interviews_nous_donnerons_les_clés_pour_prendre_en_charge_vos_infrastructures_de_manière_efficienteUn_accompagnement_particulier_sera_porté_dans_le_positionnement_dune_offre_de_services_alignée_sur_les_valeurs_du_Numérique_Responsable_Infogérer__Superviser__administrer_Linfogérance_de_votre_Système_dInformations_par_nos_services_permet_une_maitrise_depuis_la_détection_et_le_suivi_des_incidents_jusquà_la_remédiationLexploitation_de_votre_système_sera_réalisée_par_nos_équipes_depuis_le_territoire_français_Nous_intervenons_sur_site_ou_à_distance_grâce_à_notre_réseaux_dagences_et_via_nos_intervenants_locaux_Superviser_Exploiter_Administrer_Sécuriser_Nous_confier_la_gestion_de_vos_infrastructures_IT_cest_vous_permettre_de_vous_recentrer_sur_votre_informatique_métierPour_assurer_la_conduite_du_changement_de_vos_infrastructures_et_vous_conseiller_dans_leurs_évolutions_nos_experts_mettent_à_disposition_les_informations-clés__Capacity_PlanningMise_à_jour_et_évolutionIndice_qualité_Écoresponsable_IQECybersécurité', 'Service proposé par TIBCO : DATA_IA Comment TIBCO peut Solutions_IA : FORMER_VOS_EQUIPES_Montez_en_compétences_avec_vos_équipes_sur_les_outils_dIA__Microsoft_CoPilot__Apprenez_à_prompter_à_choisir_le_LLM_adapté__Nous_sommes_certifiés_Qualiopi_INTEGRER_LIA_DANS_VOS_MÉTIERS_Déployez_des_solutions_dIA_sur_mesure_pour_automatiser_des_tâches_spécifiques_à_votre_métier__RH_Finance_CommerceDe_la_création_de_contenu_à_la_gestion_des_opérations_nous_intégrons_des_IA_pour_optimiser_vos_performances_et_améliorer_vos_processus_décisionnels_CREER_VOTRE_LLM_SOUVERAIN_Bénéficiez_de_modèles_de_langage_LLM_souverains_et_sécurisés_hébergés_localement_ou_dans_des_environnements_de_confiance_pour_garantir_la_maîtrise_de_vos_données_et_la_conformité_aux_exigences_de_souveraineté_numérique_Ces_modèles_dIA_sont_configurés_pour_répondre_à_des_besoins_métier_spécifiques_tout_en_assurant_une_confidentialité_totale', 'Service proposé par TIBCO : Réseau Comment TIBCO peut Construire_un_réseau_durable : Construire_un_réseau_durable_Préparer_et_adapter_vos_réseaux_de_demain_Analyser_lexistant_Suite_à_la_collecte_de_votre_contexte_technique_la_compréhension_de_vos_enjeux_et_de_votre_organisation_interne_nos_experts_analysent_votre_infrastructure_réseauCes_données_permettent_de_formaliser_une_étude_autour_des_thèmes_suivants__Capacité_sécurité_performance_organisation_disponibilité_mobilité_sobriété_numérique_et_inter_connectivité_Définir_les_solutions_En_sappuyant_sur_les_résultats_de_lanalyse_et_de_votre_existant_nos_consultants_préconisent_avec_vos_équipes_des_solutions_permettant_doptimiser_de_faire_évoluer_ou_de_remplacer_votre_infrastructure_réseauNos_experts_sattachent_à_vous_proposer_la__juste_solution_cest-à-dire_le_meilleur_équilibre_entre__performance_technique_évolutivité_sécurité_et_budget_Intégrer__Installer__Déployer_De_la_fourniture_à_lintégration_au_sein_dinfrastructures_centrales_puis_linstallation_et_le_déploiement_sur_lensemble_de_vos_sites_distants_partout_en_France_nous_assurons_un_processus__bout_en_bout__via_une_gouvernance_et_un_acteur_unique_Piloter_Lors_des_points_opérationnels_les_équipes_abordent_les_sujets_suivants_Planification_et_prise_de_rendez-vousSuivi_des_installationsInformations_journalières_des_actions_réalisées_par_Tibco__Stock_disponible_des_équipements_et_des_accessoires_intègre_les_stocks_en_alerte_équipements_installés_sur_siteSurveillance_des_engagements']Il faudra dé-commenter la ligne suivante et supprimer la ligne "liste_services = []".
    Elle est intégrée dans prompt_generator_func de prompt_generator.py.   
    
    '''
    liste_services = recommandations_services(actu_client, news_secteur, wikipedia_text, contexte, all_services_TIBCO)
    


    # Envoi de toutes les informations nécéssaires à la génération du prompt 
    if self_prompt_yn == "Yes" and self_prompt != "":
        selected_blocks = self_prompt.split(",")
        prompt = prompt_custom(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur, selected_blocks)
    else:
        prompt = prompt_generator_func(entreprise_nom, collab_nom, liste_services, contexte, secteur, actu_client, news_secteur)
    
    
    client = OpenAI(
    api_key=OPENAI_API_KEY,
    )    
    def chat_gpt_final(prompt):
        '''
        Génération du rapport final à partir de prompt
        '''
        response = client.chat.completions.create(
            
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5 # La température à 0.5 permet un peu plus de chaleur dans le rapport
        )
        return response.choices[0].message.content.strip()

    # Envoi du prompt à ChatGPT et récupération de la réponse
    response_text = chat_gpt_final(prompt)
    

    # Création de l'ID du rapport   
    def getCode(length=5, char=string.ascii_uppercase + string.digits + string.ascii_lowercase):
        # Génère la partie aléatoire
        random_part = ''.join(random.choice(char) for _ in range(length))
        # Génère l'horodatage au format AAAAMMJJhhmmss
        timestamp = dt.now().strftime("%Y%m%d%H%M%S")
        # Concatène les deux parties
        return random_part + timestamp

ID_rapport = getCode()

    #Envoi du mail      
    send_mail_func(entreprise_nom, relation_sql, response_text, ID_rapport, destinataires, linkedin_url, reponse_relation_sql, wikipedia_text, resume_inputs, code_postal)

    #Sauvegarde du rapport dans HA-DWH
    sauvegarde_rapport_func(entreprise_nom, ID_rapport, response_text, destinataire_str, contexte)

def fonction_principale():
   
    Query_GPT(entreprise_nom, OPENAI_API_KEY,PINECONE_INDEX_NAME)

if __name__ == '__main__':
    fonction_principale()
