import os
import re
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    )   


def recommandations_services(actu_client, news_secteur, wikipedia_text, contexte, all_services_TIBCO):
    """
    Envoie à GPT-4o un résumé d'une entreprise (E1) et la liste des services proposés par ton entreprise (E0).
    Retourne une liste Python réelle de services pertinents pour l'entreprise E1.
    """
    from ast import literal_eval  # Pour convertir en liste Python
    import traceback    

    wikipedia_block = f"<p>{wikipedia_text}</p>" if wikipedia_text else ""

    prompt_system = (
        "Tu es un expert en stratégie commerciale B2B. Ton objectif est d'aider une entreprise à identifier "
        "les services qu'elle pourrait vendre à un prospect donné."
    )

    prompt_user = (
        
        f"Voici l'actualité d'une entreprise cliente potentielle (E1) :\n\n{actu_client}\n\n"
        f"Voici l'actualité du secteur de cette entreprise (E1) :\n\n{news_secteur}\n\n"
        f"Voici le contexte dans lequel notre entreprise (E0) démarche l'entreprise E1 : {contexte}"
        f"Voici la liste des services que notre entreprise (E0) propose :\n\n{all_services_TIBCO}\n\n"
        
        "Dresse une liste des 5 services de E0 qui sont les plus susceptibles d'intéresser E1, "
        "en te basant sur son activité, ses enjeux, ou son positionnement. "
        "Retourne **uniquement** une **liste Python**, sans commentaire ni texte autour."
        "Attention : les élements de la liste sont des chaînes de caractère plutôt longues, **ne les TRONQUE PAS**, c'est important."
        "Ne rajoute aucun texte avant ou après la liste, même pour expliquer."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            temperature=0
        )

        raw_output = response.choices[0].message.content.strip()
        raw_output = re.sub(r"^```python\s*|```$", "", raw_output.strip(), flags=re.MULTILINE).strip()

        # Sécuriser la conversion en liste Python
        try:
            result = literal_eval(raw_output)
            if isinstance(result, list):
                return result
                print(result)
            else:
                print("⚠️ Le résultat n'est pas une liste. Voici le texte brut :")
                print(raw_output)
                return []
        except Exception:
            print("⚠️ Impossible de parser la sortie comme liste Python.")
            print("Réponse brute :\n", raw_output)
            return []

    except Exception as e:
        print("❌ Erreur lors de la requête OpenAI :")
        traceback.print_exc()
        return []
