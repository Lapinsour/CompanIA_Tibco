import pyodbc 

def liste_client():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=HA-DWH;''DATABASE=TIBCOVIEW_TS;''Trusted_Connection=yes')

    cursor = conn.cursor()
    cursor.execute("""
                    SELECT DISTINCT NOM1_CLI FROM CLIENT ORDER BY NOM1_CLI
            """)

    
    clients = [row[0] for row in cursor.fetchall()]
    
    
    conn.close()
    
    
    return clients