import asyncio
from playwright.async_api import async_playwright
from newspaper import Article
import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



async def scrape_bing_news(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Simuler un vrai utilisateur avec un User-Agent
        page.set_default_timeout(10000)
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})

        # Ouvrir Bing News
        url = f"""https://www.bing.com/news/search?q=Secteur+{query.replace(' ', '+')}+actualités&qft=interval%3d"9"&form=PTFTNR"""
        await page.goto(url)
        await page.wait_for_timeout(3000)  

        articles = []
        # Sélectionner tous les articles
        news_items = (await page.query_selector_all("div.news-card.newsitem"))[:50]  

        for item in news_items:
            try:
                # Récupérer le titre et le lien
                title_element = await item.query_selector("a.title")
                title = await title_element.inner_text() if title_element else "Titre inconnu"
                link = await title_element.get_attribute("href") if title_element else None
                
                # Vérifier si le lien est valide
                if not link or not link.startswith("http"):
                    continue  # Ignorer si le lien est invalide

                # Récupérer la source
                source_element = await item.query_selector(".source")
                source = await source_element.inner_text() if source_element else "Source inconnue"

                # Récupérer la date
                date_element = await item.query_selector("span[aria-label]")
                date = await date_element.get_attribute("aria-label") if date_element else "Date inconnue"

                # Récupérer l'extrait (snippet)
                snippet_element = await item.query_selector(".snippet")
                chapo = await snippet_element.inner_text() if snippet_element else "Pas d'extrait disponible"

                # Si snippet est vide, essayer avec newspaper3k pour obtenir un extrait complet
                
                snippet = get_article_content(link)

                # Ajouter l'article à la liste
                articles.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "date": date,
                    "chapi":chapo,
                    "snippet": snippet
                })
            except Exception as e:
                
                continue  # Ignorer les erreurs et continuer

        await browser.close()
        return articles

def get_article_content(url):
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:1000]  # Retourne les 500 premiers caractères
    except Exception as e:        
        return "Impossible de récupérer le contenu"

client = OpenAI(
    api_key=OPENAI_API_KEY,
    )

# Fonction pour interroger ChatGPT
def chat_gpt(prompt):
    response = client.chat.completions.create(        
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()



def rag_secteur_func(secteur):
    news = asyncio.run(scrape_bing_news(f'{secteur}'))
    prompt = f"Voici une sélection d'articles sur le {secteur}."
    
    for article in news:
        prompt+= str(article)
        
    prompt+= f"A partir de cette sélection, résume en 1000 signes l'actualité du {secteur}.\
        Accorde la priorité à l'actualité concernant la France et l'Europe.\
        Accorde plus d'importance aux actualités relatives à la cybersécurité, la Data, le numérique, la mise en réseau ou encore la réutilisation de composants électroniques."
    response_text = chat_gpt(prompt)
    
    
    return response_text



if __name__ == '__main__':
    rag_secteur_func()
