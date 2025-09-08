<<<<<<< HEAD
# CompanIA



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.tibco.fr/DSN-DECISIONNEL/compania.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.tibco.fr/DSN-DECISIONNEL/compania/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
=======
#COMPANIA
CompanIA est une application qui : 
- génère un prompt à partir des entrées d'un formulaire et enrichi par du RAG basé : 
        - sur des informations sur les offres de services Tibco stockées dans une BDD vectorielle Tibco
        - sur les actualités de l'entreprise qui fait l'objet de l'entretien et de son secteur récupérées via webscraping et l'API NewsAPI, 
- requête ce prompt à l'api OpenAI afin de générer un brief de préparation d'entretien commercial, 
- puis envoie la réponse du LLM ainsi que des informations récupérées sur les BDD Tibco sous forme de mail au(x) destinataire(s) sélectionné(s), 
- en ajoutant en pièce jointe un fichier résumant les contrats dont dispose Tibco avec l'entreprise qui fait l'objet de l'entretien ainsi qu'une version text-to-speech du brief.

CompanIA est destinée à la cinquantaine de commerciaux Tibco. L'accès au formulaire leur est conférée par la SI, via le groupe de sécurité Azure des commerciaux. 
Le schéma de la V1 de l'application est accessible au lien suivant : https://tibcodf.atlassian.net/wiki/spaces/R2D/pages/962166785/CompanIA
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

-- NOTE : actualisation_actu_pinecone_script.py ne fait pas directement partie de l'application. Il est exécuté chaque semaine sur srv-scripts-to. Il purge la BDD vectorielle Pinecone des vieilles actus des entreprises et rafraîchit ces actualités en lançant un webscraping pour chaque entreprise présente dans la BDD Pinecone (celles qui ont déjà fait l'objet de rapports.)
>>>>>>> 65f3611 (Mise à jour du projet avec nouvelle version testée en local)
