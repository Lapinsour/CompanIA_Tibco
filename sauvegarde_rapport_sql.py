import pyodbc 
from datetime import datetime

def sauvegarde_rapport_func(entreprise_nom, ID_rapport, response_text, destinataire, contexte):

    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=HA-DWH;''DATABASE=COMPANIA;''Trusted_Connection=yes')
    cursor = conn.cursor()

    # Variables Python à insérer
    ENTREPRISE_RAPPORT = entreprise_nom
    
    DATE_RAPPORT = datetime.today().strftime('%Y-%m-%d')
    
    IDENT_RAPPORT = ID_rapport
    TEXTE_RAPPORT = response_text[:3000]
    MAIL_USER = destinataire
    CONTEXTE = contexte
    

    # Requête SQL d'insertion
    cursor.execute("""
        INSERT INTO RAPPORTS_COMPANIA (IDENT_RAPPORT,DATE_RAPPORT,MAIL_USER,TEXTE_RAPPORT,ENTREPRISE_RAPPORT)
        VALUES (?, ?, ?, ?,?)
    """, (IDENT_RAPPORT,DATE_RAPPORT,MAIL_USER,TEXTE_RAPPORT,ENTREPRISE_RAPPORT))

    # Valider et fermer la connexion
    conn.commit()
    cursor.close()
    conn.close()