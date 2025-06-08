import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import time
import re


def check_page_exists(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def parse_scholar(query, pages=10, from_year=None, to_year=None, sort_by=None):
    results_list=[]
    for i in range(pages):
        if i == 0:
            base_url = "http://www.scholar.ru/search.php?q="
            encoded_query = quote_plus(query)
            search_url = base_url + encoded_query
            parse_page(search_url, from_year, to_year)
        else:
            base_url = "http://www.scholar.ru/search.php?page="+str(i)+"&q="
            encoded_query = quote_plus(query)
            search_url = base_url + encoded_query
            if check_page_exists(search_url):
                results_list.append(parse_page(search_url, from_year, to_year))
    results_list = [item for sublist in results_list for item in sublist]
    if sort_by=='author':
        # Сортировка по автору (по алфавиту)
        results_list = sorted(results_list, key=lambda x: x['authors'])
    if sort_by=='year':
        # Сортировка по году (сначала свежее)
        results_list = sorted(results_list, key=lambda x: x['year'], reverse=True)
    return results_list


def parse_page(search_url, from_year, to_year):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    time.sleep(1)  # вежливая задержка
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = soup.find_all('div', class_='result-pub')
    articles = []
    for result in results:
        title = result.find('a', href = 'javascript://').get_text()
        authors, year = extract_authors_and_year(result.find('span', class_='r_authors').get_text())

        # Пропускаем, если год не найден
        try:
            year_int = int(year)
        except ValueError:
            continue  # пропускаем запись, если год не год

        if from_year or to_year:
            if from_year and from_year!='all':
                if not year_int>int(from_year): continue
            if to_year and to_year!='all':
                if not year_int<int(to_year): continue
        annotation = result.find('div', class_='js-ann-short').get_text()
        annotation = ' '.join(annotation.split())[:2300]+'...' if len(' '.join(annotation.split()))>2400 else ' '.join(annotation.split())
        url = result.find('a', rel='nofollow')['href']
        articles.append({'title': title, 'authors': authors, 'year': year, 'abstract': annotation, 'url': url})

    return articles


def extract_authors_and_year(text):
    cleaned = ' '.join(text.split())
    # Ищем год в конце строки
    year_match = re.search(r'(\d{4})$', cleaned)
    year = year_match.group(1) if year_match else ""
    # Убираем всё после года
    if year:
        cleaned = cleaned.rsplit(year, 1)[0].strip()
    # Если строка начинается с дефиса — автора нет
    if cleaned.startswith('-') or cleaned == '':
        authors = "Не найдено"
    elif ' - ' in cleaned:
        authors = cleaned.split(' - ')[0].strip()
        if not authors:
            authors = "Не найдено"
    else:
        # Если нет " - ", пробуем отрезать до первой запятой
        authors = cleaned.split(',')[0].strip()
        if not authors or authors == cleaned:
            authors = "Не найдено"
    return authors, year


#articles = parse_scholar(query, from_year=2010, to_year=2012, sort_by='author')

#print(articles)

