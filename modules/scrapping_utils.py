import re
import datetime
import asyncio
from playwright.async_api import async_playwright
from newspaper import Article
from modules.pinecone_utils import upsert_article_in_pinecone, extract_liste_entreprise_nom, check_for_actu_in_pinecone, refresh_actu

# ========================
# UTILITAIRES DATES
# ========================

mois_fr_vers_en = {
    "janv.": "Jan", "févr.": "Feb", "mars": "Mar", "avr.": "Apr", "mai": "May", "juin": "Jun",
    "juil.": "Jul", "août": "Aug", "sept.": "Sep", "oct.": "Oct", "nov.": "Nov", "déc.": "Dec"
}

def convertir_date_relative(date_str):
    """Convertit une date relative (ex: 'il y a 2 jours') en date absolue."""
    date_str = date_str.replace("\xa0", " ")
    today = datetime.datetime.now()

    match = re.match(r"il y a (\d+) (jour|jours|semaine|semaines|mois|heure|heures)", date_str, re.IGNORECASE)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)

        if "jour" in unit:
            return today - datetime.timedelta(days=amount)
        elif "semaine" in unit:
            return today - datetime.timedelta(weeks=amount)
        elif "mois" in unit:
            return today - datetime.timedelta(days=amount * 30)
        elif "heure" in unit:
            return today - datetime.timedelta(hours=amount)
    return None


def convertir_mois_fr_en(date_str):
    for mois_fr, mois_en in mois_fr_vers_en.items():
        date_str = date_str.replace(mois_fr, mois_en)
    return date_str


def convertir_date_texte(date_str):
    """Convertit une date texte en objet datetime."""
    date = convertir_date_relative(date_str)
    if date:
        return date
    date_str = convertir_mois_fr_en(date_str)
    try:
        return datetime.datetime.strptime(date_str, "%d %b %Y")
    except ValueError:
        return None

# ========================
# SCRAPING
# ========================

async def scrape_bing_news(query, secteur):
    """Scraping Bing News via Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(10000)
        await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})

        url = f"""https://www.bing.com/news/search?q="{query.replace(' ', '+')}"&qft=interval%3d"9"&form=PTFTNR"""
        await page.goto(url)
        await page.wait_for_timeout(3000)

        articles = []
        news_items = await page.query_selector_all("div.news-card.newsitem")

        for item in news_items:
            try:
                title_element = await item.query_selector("a.title")
                title = await title_element.inner_text() if title_element else "Titre inconnu"
                link = await title_element.get_attribute("href") if title_element else None
                if not link or not link.startswith("http"):
                    continue

                source_element = await item.query_selector(".source")
                source = await source_element.inner_text() if source_element else "Source inconnue"

                date_element = await item.query_selector("span[aria-label]")
                date = await date_element.get_attribute("aria-label") if date_element else "Date inconnue"

                snippet_element = await item.query_selector(".snippet")
                chapo = await snippet_element.inner_text() if snippet_element else "Pas d'extrait disponible"

                snippet = get_article_content(link)

                articles.append({
                    "title": title,
                    "url": link,
                    "source": source,
                    "date": date,
                    "chapo": chapo,
                    "snippet": snippet
                })
            except Exception:
                continue

        await browser.close()
        return articles


def get_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text[:1000]
    except Exception:
        return "Impossible de récupérer le contenu"


def google_news_scrap(PINECONE_API_KEY, PINECONE_INDEX_NAME, model_name, entreprise_nom, secteur):
    """Scraping + insertion dans Pinecone si l'entreprise est nouvelle."""
    articles = []
    all_entreprises = extract_liste_entreprise_nom(PINECONE_API_KEY, PINECONE_INDEX_NAME)
    liste_entreprises = [element.lower() for element in all_entreprises]

    if entreprise_nom.lower() in liste_entreprises:
        return check_for_actu_in_pinecone(PINECONE_API_KEY, entreprise_nom, model_name, PINECONE_INDEX_NAME, "recherche actus client")

    news = asyncio.run(scrape_bing_news(f'{entreprise_nom}', secteur))

    for article in news:
        articles.append({
            "titre_article": article['title'],
            "date": convertir_date_texte(article['date']).strftime("%Y-%m-%d") if convertir_date_texte(article['date']) else None,
            "texte_article": article['snippet'],
            "nom_entreprise": entreprise_nom,
            'source': article['url']
        })

    for article in articles:
        if article["date"] is not None:
            upsert_article_in_pinecone(PINECONE_API_KEY, PINECONE_INDEX_NAME, model_name, article)

    refresh_actu(PINECONE_API_KEY, PINECONE_INDEX_NAME, 90)
    return check_for_actu_in_pinecone(PINECONE_API_KEY, entreprise_nom, model_name, PINECONE_INDEX_NAME, "recherche actus client")
