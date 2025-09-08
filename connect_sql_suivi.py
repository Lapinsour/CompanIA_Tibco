
import pyodbc
import sys


id_rapport = sys.argv[1]
note_satisfaction = sys.argv[2]
temps_gagne = 0
commentaire = "no comment"


def insert_suivi(id_rapport, note_satisfaction, temps_gagne):

    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=HA-DWH;''DATABASE=COMPANIA;''Trusted_Connection=yes')

    cursor = conn.cursor()

    # Requête SQL d'insertion
    cursor.execute("""
        INSERT INTO [dbo].[SUIVI_UTILISATEUR_COMPANIA] (IDENT_RAPPORT, NOTE_SATISFACTION_RAPPORT, TEMPS_GAGNE_RAPPORT)
        VALUES (?, ?, ?)
    """, (id_rapport, note_satisfaction, temps_gagne))

    # Valider et fermer la connexion
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == '__main__':
    insert_suivi(id_rapport, note_satisfaction, temps_gagne)