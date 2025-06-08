import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time

def search_neb(query, max_results=50):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    base_url = "https://rusneb.ru/search/?q="
    encoded_query = quote_plus(query)
    search_url = base_url + encoded_query

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for card in soup.select("a[href^='/catalog/']"):
        text = card.text.lower()
        full_url = "https://rusneb.ru" + card['href']

        if "диссертац" in text and full_url not in links:
            links.append(full_url)

        if len(links) >= max_results:
            break

    return links



def parse_neb_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    time.sleep(1)  # вежливая задержка
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    def get_meta(name=None, prop=None):
        tag = soup.find("meta", attrs={"name": name}) if name else soup.find("meta", attrs={"property": prop})
        return tag['content'].strip() if tag and tag.get('content') else 'Не найдено'

    # Ищем элемент с id="toClipBoard" и вытаскиваем содержимое <span class="span_strong">
    biblio_block = soup.find('div', id='toClipBoard')
    author = "Не найдено"
    if biblio_block:
        author_span = biblio_block.find('span', class_='span_strong')
        if author_span:
            author = author_span.get_text(strip=True)

    return {
        "title": get_meta(prop="og:title"),
        "authors": author,
        "year": get_meta(prop="book:release_date"),
        "abstract": get_meta(prop="og:description"),
        "url": url
    }


def parse_neb(query, from_year=None, to_year=None, sort_by=None):
    result_links = search_neb(query, max_results=100)
    articles = []
    for link in result_links:
        article_data = parse_neb_article(link)

        if not article_data:
            continue
            # Преобразуем год в число и фильтруем
        try:
            year = int(article_data['year'])
            if (from_year and year < from_year) or (to_year and year > to_year):
                continue
        except (ValueError, TypeError):
            continue  # Пропускаем, если год не число

        articles.append(article_data)

    if sort_by=='author':
        # Сортировка по автору (по алфавиту)
        articles = sorted(articles, key=lambda x: x['authors'])
    if sort_by == 'year':
        # Сортировка по году (сначала свежее)
        articles = sorted(articles, key=lambda x: x['year'], reverse=True)
    return articles

# Пример использования
#query = "автоматический поиск литературы"

#print(parse_neb(query, from_year=2010, to_year=2020, sort_by='author'))