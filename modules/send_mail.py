import re
import smtplib
from email.message import EmailMessage
from gtts import gTTS
from bs4 import BeautifulSoup
from openai import OpenAI
import os 


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def send_mail_func(entreprise_nom, relation_sql, response_text, ID_rapport, destinataires, linkedin_url, reponse_relation_sql, wikipedia_text, resume_inputs, liste_services):
    

    # === Helper : conversion Markdown-like vers HTML
    def markdown_to_html(text):
        text = re.sub(r'(?m)^### (.+)', r'<h3>\1</h3>', text)
        text = re.sub(r'(?m)^#### (.+)', r'<h4>\1</h4>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'(?m)^(\d+\.\s)(.+)', r'<strong>\1\2</strong>', text)
        return text.replace("\n", "<br>")

    # === Génération du contenu HTML
    response_text_html = markdown_to_html(response_text)

    wikipedia_block = f"<p>{wikipedia_text}</p>" if wikipedia_text else ""

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h3 {{ color: #333366; }}
            h4 {{ color: #555555; }}
            strong {{ color: #000000; }}
        </style>
    </head>
    <body>
        <p>Bonjour,</p>
        <p>Voici votre brief préparatoire à votre entretien avec l'entreprise {entreprise_nom}.</p>
        <p>{resume_inputs}</p>
        <p>Vous voulez vous connecter avec votre interlocuteur.ice ? 
            <a href="{linkedin_url}">Cliquez ici pour accéder à sa page LinkedIn !</a>
        </p>        
        <p>LS = {liste_services}</p>
        <p>{reponse_relation_sql}</p>
        {wikipedia_block}
        {response_text_html}
        <p>Vous trouverez en pièce jointe la retranscription audio de ce rapport.</p>
        <p>Je vous souhaite un excellent entretien !</p>        
        <p>Cordialement,\n<strong>CompanIA, votre compagnon commercial by Tibco :)</strong></p>
        <p><em>PS : Vous voulez nous faire part d'un commentaire ou d'une piste d'amélioration quant à l'outil CompanIA ? Nous sommes à votre écoute ! Remplissez le formulaire de suivi, 
        en renseignant le code {ID_rapport}.</em></p>
    </body>
    </html>
    """

    # === Extraction texte pour TTS & Humanisation
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text(separator="\n")

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        )
    def humanisation(text_content):
        brief = "Tu es un commercial expérimenté qui explique un brief client à un collègue.\
              Rends le ton naturel, oral et vivant. Mais reste professionnel. Tu peux ajouter des des pauses, et des tournures dynamiques. Sois clair, structuré mais pas trop formel. Voici le brief :\n"
        brief+= text_content       
        response = client.chat.completions.create(        
            model="gpt-4o",
            messages=[
                    {"role": "user", "content": brief}
                ],
            temperature = 0.5
        )
        return response.choices[0].message.content.strip()
    

    brief_humain = humanisation(text_content)

    # === Génération audio (gTTS)
    audio_file = "votre_rapport.mp3"
    tts = gTTS(text=brief_humain, lang='fr')
    tts.save(audio_file)

    # === Configuration SMTP
    SMTP_SERVER = "smtprelais.tibco.fr"
    SMTP_PORT = 25
     
    # === Création de l'email
    msg = EmailMessage()
    msg["Subject"] = f"Votre brief sur {entreprise_nom}, par CompanIA"
    msg["From"] = "compania@tibco.fr"
    

    msg.set_content(text_content)                      # version texte
    msg.add_alternative(html_content, subtype='html')  # version HTML

    # === Pièce jointe CSV si présente
    if relation_sql:
        msg.add_attachment(
            relation_sql.encode('utf-8'),
            maintype='text',
            subtype='csv',
            filename='export_affaires.csv'
        )

    # === Pièce jointe audio
    with open(audio_file, 'rb') as f:
        msg.add_attachment(
            f.read(),
            maintype='audio',
            subtype='mpeg',
            filename=audio_file
        )

    for destinataire in destinataires : 
        msg["To"] = destinataire
        # === Envoi du mail
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.send_message(msg)
                print("Email envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
        del msg["To"]
