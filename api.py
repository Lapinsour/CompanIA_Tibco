from flask import Flask, request, render_template, redirect, url_for
import subprocess
from liste_clients_tibco import liste_client
import nltk
from nltk.data import find
from liste_id_rapport_suivi import liste_id_rapport
import threading
import ssl
from logging_config import logger

def safe_download(package):
    try:
        find(package)
    except LookupError:
        nltk.download(package)

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
    except:
        logger.error(f"Erreur lors de la récupération des clients : {e}")
        return render_template('formulaire.html', clients=[0])

def lancer_script_en_arriere_plan(*args):
    try:
        subprocess.run([
            "C:\Program Files\Python\Python313\python.exe", "script.py", *args
        ])    
        logger.info("Script lancé en arrière-plan avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du lancement du script : {e}")


@app.route('/run-script', methods=['POST'])
def run_script():
    # Récupération des valeurs du formulaire
    entreprise_nom = request.form.get('entreprise_nom', '')
    secteur = request.form.get('secteur_entreprise', '')
    contexte = request.form.get('contexte', '')
    collaborateur_nom = request.form.get('collaborateur_nom', '')
    collaborateur_fonction = request.form.get('collaborateur_fonction','')
    destinataire = request.form.get('destinataire', '')
    autre = request.form.get('autre','')

    # Récupération des cases cochées sous forme de liste
    choix = request.form.getlist('choix')
    choix_str = ",".join(choix)  

     

    # Exécution du script Python avec tous les paramètres
    thread = threading.Thread(target=lancer_script_en_arriere_plan, args=(
        entreprise_nom, secteur, contexte, collaborateur_nom, destinataire, choix_str, email_utilisateur, collaborateur_fonction, autre
    ))
    thread.start()
    
    return redirect(url_for('suivi_feedback'))

@app.route("/suivi", methods=['GET', 'POST'])
def suivi_feedback():
    if request.method == 'POST':
        id_rapport = request.form.get('id_rapport', '')
        note_satisfaction = request.form.get('rating_etoiles', '')

        subprocess.run([
            "C:\Program Files\Python\Python313\python.exe", "connect_sql_suivi.py", id_rapport, note_satisfaction
        ])
        return render_template("suivi_confirmation.html")

    # Si GET → afficher le formulaire (avec datalist ou autre)
    all_id = liste_id_rapport()
    return render_template("suivi_form.html", all_id=all_id)

    

    

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='C:/Certificats/tibco_fr.crt', keyfile='C:/Certificats/tibco_fr.key')
    app.run(ssl_context=context, host='0.0.0.0', port=443, debug=True)
    print("Run en cours...")