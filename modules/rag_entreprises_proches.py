import pyodbc 
import pandas as pd
import io
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

def rag_entreprises_proches(code_postal):
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=HA-DWH;'
        'DATABASE=TIBCOVIEW_TS;'
        'Trusted_Connection=yes'
    )

    query = """
        WITH table_proximite AS (
            SELECT * FROM (
                SELECT TOP (30) *, 1 AS PROXIMITE
                FROM CLIENT
                WHERE CODE_POSTAL_CLI = (?)
                UNION
                SELECT TOP (30) *, 2 AS PROXIMITE
                FROM CLIENT
                WHERE NOT CODE_POSTAL_CLI = (?)
                AND LEFT(CODE_POSTAL_CLI, 3) = LEFT((?), 3)
                UNION
                SELECT TOP (30) *, 3 AS PROXIMITE
                FROM CLIENT
                WHERE NOT LEFT(CODE_POSTAL_CLI, 3) = LEFT((?), 3)
                AND LEFT(CODE_POSTAL_CLI, 2) = LEFT((?), 2)
                ORDER BY PROXIMITE, CODE_POSTAL_CLI
            ) AS RESULT
        ),
        table_aff_en_cours AS (
            SELECT * 
            FROM AFFAIRE
            WHERE DATE_FIN_R_AFF IS NULL
        ),
        table_cli_aff_en_cours AS (
            SELECT C.CODE_CLI, C.NOMAPPEL_CLI, A.IDENT_AFF, A.CODE_ACTIVITE_AFF, 
                   A.ACTIVITE_AFF, A.DATE_CREATION_AFF
            FROM CLIENT C
            INNER JOIN table_aff_en_cours A ON C.CODE_CLI = A.CODE_CLIENT_AFF
        )
        SELECT TOP(10) P.CODE_POSTAL_CLI, P.PROXIMITE, P.CODE_CLI, P.NOM1_CLI, 
               Z.TYPOLOGIE_ENTREPRISE_CLIZL, P.FAMILLE_CLI, P.VILLE_CLI, P.ADRESSE_CLI, 
               A.IDENT_AFF, A.CODE_ACTIVITE_AFF, A.ACTIVITE_AFF, A.DATE_CREATION_AFF
        FROM table_proximite P
        INNER JOIN table_cli_aff_en_cours A ON P.CODE_CLI = A.CODE_CLI
        LEFT JOIN CLIENT_ZL Z ON P.IDENT_CLI = Z.IDENT_CLI_CLIZL
        ORDER BY PROXIMITE, P.CODE_CLI
    """

    params = (code_postal, code_postal, code_postal, code_postal, code_postal)
    df = pd.read_sql(query, conn, params=params)

    # Prépare la sortie CSV en mémoire
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    csv_content = buffer.getvalue()

    if df.empty:
        phrase = "Tibco ne travaille avec aucune entreprise dans le secteur géographique de cette entreprise."
    else:
        nb_clients = df["NOM1_CLI"].nunique()
        familles = df["FAMILLE_CLI"].dropna().unique().tolist()
        familles_str = ", ".join(familles)
        
        phrase = (
            f"Dans le secteur géographique de cette entreprise, "
            f"Tibco a des affaires en cours avec {nb_clients} "
            f"client(s), dans les secteurs suivants : {familles_str}."
        )

    return phrase, csv_content
