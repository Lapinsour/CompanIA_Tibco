import pyodbc 

def liste_id_rapport():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=REC-DECIS;''DATABASE=COMPANIA;''Trusted_Connection=yes')

    cursor = conn.cursor()
    cursor.execute("""                    
        SELECT DISTINCT IDENT_RAPPORT 
        FROM RAPPORTS_COMPANIA 
        WHERE  IDENT_RAPPORT NOT IN (SELECT DISTINCT IDENT_RAPPORT FROM SUIVI_UTILISATEUR_COMPANIA)
            """)

    
    all_id_rapport = [row[0] for row in cursor.fetchall()]
    
    
    conn.close()
    
    
    return all_id_rapport