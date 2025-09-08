import pyodbc 
import csv
from io import StringIO

def rag_sql_tibco(entreprise_nom):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=HA-DWH;''DATABASE=TIBCOVIEW_TS;''Trusted_Connection=yes')

    cursor_table_csv = conn.cursor()
    query = """
        SELECT 
        IDENT_AFF AS 'Identifiant affaire',
        NOM_AFFAIRE_AFF AS 'Nom affaire',
        BUDGET_AFFAIRE_AFF AS 'Budget affaire',
        DATE_CREATION_AFF AS 'Création affaire',
        DATE_FIN_R_AFF AS 'Fin affaire',
        NOM_CLIENT_AFF AS 'Client affaire',
        CLIENT.SIRET_CLI AS 'Siret',
        SUM(FACTURE_CLIENT.HT_EN_EUR_FACT) AS 'Facture affaire'
    FROM CLIENT
    LEFT JOIN AFFAIRE ON CLIENT.CODE_CLI = AFFAIRE.CODE_CLIENT_AFF
    LEFT JOIN FACTURE_CLIENT ON FACTURE_CLIENT.AFFAIRE_FACT = AFFAIRE.CODE_AFFAIRE_AFF
    WHERE UPPER(CLIENT.NOM1_CLI) LIKE UPPER(?)
    GROUP BY 
        IDENT_AFF, NOM_AFFAIRE_AFF, BUDGET_AFFAIRE_AFF, DATE_CREATION_AFF, DATE_FIN_R_AFF, NOM_CLIENT_AFF, CLIENT.SIRET_CLI
    ORDER BY DATE_CREATION_AFF DESC
        """

    cursor_table_csv.execute(query,(f"{entreprise_nom}",))

    # Récupérer les résultats
    rows = cursor_table_csv.fetchall()

    type_date = None
    derniere_date = None 

    if rows:
        # Récupération des noms de colonnes
        columns = [column[0] for column in cursor_table_csv.description]  

        col_names = [col.lower() for col in columns]
        idx_ident_aff = col_names.index("identifiant affaire".lower())
        idx_facture = col_names.index("facture affaire".lower())
        idx_budget = col_names.index("budget affaire".lower())
        idx_date_creation = col_names.index("création affaire".lower())
        idx_date_fin = col_names.index("fin affaire".lower())
        idx_siret = col_names.index("siret")

        # Extraire le(s) SIRET(s)
        sirets = list({row[idx_siret] for row in rows if row[idx_siret] is not None})       
        siret = sirets[0] if sirets else None
        print("SIRET : ", siret)

        # Vérifier si toutes les lignes ont IDENT_AFF à None
        all_ident_null = all(row[idx_ident_aff] is None for row in rows)

        if all_ident_null:
            nb_aff = 0
            nb_aff_en_cours = 0
            total_facture = 0
            total_budget = 0
        else:
            nb_aff = sum(1 for row in rows if row[idx_ident_aff] is not None)
            nb_aff_en_cours = sum(1 for row in rows if row[idx_date_fin] is None and row[idx_ident_aff] is not None)
            total_facture = sum(row[idx_facture] or 0 for row in rows if row[idx_ident_aff] is not None)
            total_budget = sum(row[idx_budget] or 0 for row in rows if row[idx_ident_aff] is not None)

            # Détermination de la date la plus pertinente
            all_fin_non_null = all(row[idx_date_fin] is not None for row in rows if row[idx_ident_aff] is not None)

            if all_fin_non_null:
                type_date = "fin"
                dates_fin = [row[idx_date_fin] for row in rows if row[idx_date_fin] is not None]
                derniere_date = max(dates_fin) if dates_fin else None
            else:
                type_date = "création"
                dates_creation = [row[idx_date_creation] for row in rows if row[idx_date_creation] is not None]
                derniere_date = max(dates_creation) if dates_creation else None

            derniere_date = derniere_date.strftime("%d-%m-%Y")

        # Génération du CSV
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(columns)
        writer.writerows(rows)
        output.seek(0)

        return output.getvalue(), nb_aff, nb_aff_en_cours, total_budget, total_facture, siret, type_date,derniere_date

    else:
        return None
    







def liste_client_rag():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};''SERVER=HA-DWH;''DATABASE=TIBCOVIEW_TS;''Trusted_Connection=yes')

    cursor = conn.cursor()
    cursor.execute("""
                    SELECT DISTINCT NOM1_CLI FROM CLIENT ORDER BY NOM1_CLI
            """)

    
    clients = [row[0] for row in cursor.fetchall()]
    
    
    conn.close()
    
    
    return clients