from flask import Flask, request, render_template, redirect, url_for
import subprocess
from modules.liste_clients_tibco import liste_client
import nltk
from nltk.data import find
from modules.liste_id_rapport_suivi import liste_id_rapport
import threading
import ssl
from modules.logging_config import logger
import os
from dotenv import load_dotenv

load_dotenv()  

ENV_MODE = os.getenv("ENV_MODE", "local")
USE_SSL = os.getenv("USE_SSL", "false").lower() == "true"
PORT = int(os.getenv("PORT", "5000"))

# Choix du chemin Python selon le mode
PYTHON_EXECUTABLE = os.getenv("PYTHON_PATH_PROD") if ENV_MODE == "prod" else os.getenv("PYTHON_PATH_LOCAL")

def safe_download(package):
    try:
        find(package)
    except LookupError:
        nltk.download(package)

#télécharge les packages de traitement du langage (NLP) au lancement de l'application
def initialize_nltk():
    safe_download('tokenizers/punkt')
    safe_download('taggers/averaged_perceptron_tagger')
    safe_download('taggers/averaged_perceptron_tagger_eng')
    safe_download('corpora/wordnet')

app = Flask(__name__)

# Initialisation NLTK au démarrage
with app.app_context():
    initialize_nltk()

@app.route('/')
def index():
    try:
        clients = liste_client()  # Appel de la fonction pour récupérer la liste des clients
        logger.info("Page principale appelée avec succès")
        return render_template('formulaire.html', clients=clients) 
    #Charge un formulaire HTML (formulaire.html) avec une liste de clients. En cas d’erreur, affiche un formulaire vide (clients = [0]).
    except:
        logger.error(f"Erreur lors de la récupération des clients")
        return render_template('formulaire.html', clients=[0])

def lancer_script_en_arriere_plan(*args):
    #subprocess Lance script.py avec les arguments du formulaire dans un thread séparé pour ne pas bloquer le serveur web 
    #On peut lancer plusieurs requêtes en simultané et/ou remplir le formulaire de satisfaction pendant que la requête tourne
    try:
        subprocess.run([PYTHON_EXECUTABLE, "script.py", *args])
        logger.info("Script lancé en arrière-plan avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du lancement du script")


@app.route('/run-script', methods=['POST'])
def run_script():
    entreprise_nom = request.form.get('entreprise_nom', '')
    secteur = request.form.get('secteur_entreprise', '')
    contexte = request.form.get('contexte', '')
    collaborateur_nom = request.form.get('collaborateur_nom', '')    
    destinataire = request.form.get('destinataire', '')    
    code_postal = request.form.get('code_postal', '')
    self_prompt_yn = request.form.get('self_prompt_yn', 'No')

    if self_prompt_yn == "Yes":
        # On récupère les blocs cochés et on les transforme en chaîne
        selected_blocks = request.form.getlist("blocks")
        self_prompt = ",".join(selected_blocks)
    else:
        self_prompt = ""

    # Lancement du script en arrière-plan avec tous les arguments
    thread = threading.Thread(
        target=lancer_script_en_arriere_plan, 
        args=(entreprise_nom, secteur, contexte, collaborateur_nom, destinataire, code_postal, self_prompt_yn, self_prompt)
    )
    thread.start()
    
    return redirect(url_for('suivi_feedback'))

@app.route("/suivi", methods=['GET', 'POST'])
def suivi_feedback():
    if request.method == 'POST':
        id_rapport = request.form.get('id_rapport', '')
        note_satisfaction = request.form.get('rating_etoiles', '')

        subprocess.run([PYTHON_EXECUTABLE, "connect_sql_suivi.py", id_rapport, note_satisfaction])

        return render_template("suivi_confirmation.html")

    # Si GET → afficher le formulaire (avec datalist ou autre)
    all_id = liste_id_rapport()
    return render_template("suivi_form.html", all_id=all_id)    

    

if __name__ == '__main__': #Modifier le fichier .env selon si on lance en local ou prod
    if USE_SSL:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(
            certfile=os.getenv("SSL_CERT_PATH"),
            keyfile=os.getenv("SSL_KEY_PATH")
        )
        app.run(ssl_context=context, host='0.0.0.0', port=PORT, debug=(ENV_MODE != "prod"))
    else:
        app.run(host="0.0.0.0", port=PORT, debug=(ENV_MODE != "prod"))
