import requests

#все работает,фильтры есть,сортировка есть,единственный минус - мало русскоязычных, поэтому поиск на русском 50/50 релевантный
def search_openalex(query, per_page=5, from_year=None, to_year=None,
                    source_type=None, language=None, sort_by=None):

    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": per_page,
        "mailto": "scisearch058@gmail.com"
    }


    # Формируем фильтры
    filters = []
    if from_year or to_year:
        year_filter = []
        if from_year:
            year_filter.append(f"from_publication_date:{from_year}-01-01")
        if to_year:
            year_filter.append(f"to_publication_date:{to_year}-12-31")
        filters.append(",".join(year_filter))

    if source_type:
        filters.append(f"type:{source_type}")

    if language:
        filters.append(f"language:{language}")

    if filters:
        params["filter"] = ",".join(filters)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        total_count = data.get("meta", {}).get("count", 0)
        results = data.get("results", [])

        print(f"\n🔍 Найдено источников всего: {total_count}")
        print(f"📄 Показано результатов: {len(results)}\n")

        if not results:
            print(f"По запросу '{query}' ничего не найдено")
            return []

        # Создаем список словарей с данными
        articles_data = []
        for work in results:
            article = {
                "title": work.get("title", "Без названия"),
                "authors": [a['author']['display_name'] for a in work.get("authorships", [])],
                "year": work.get("publication_year", None),
                "abstract": get_abstract(work),
                "url": work.get("id", None),
                "source_type": work.get("type", None),
                "language": work.get("language", None)
            }
            articles_data.append(article)

        # Сортировка результатов
        if sort_by == 'author':
            articles_data.sort(key=lambda x: x['authors'][0] if x['authors'] else "")
        elif sort_by == 'year':
            articles_data.sort(key=lambda x: x['year'] if x['year'] else 0, reverse=True)

        return articles_data

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Ошибка при запросе: {e}")
        return []


def get_abstract(work):
    """Извлекает аннотацию из работы"""
    abstract_inv = work.get("abstract_inverted_index")
    if abstract_inv:
        return ' '.join(sorted(abstract_inv.keys(), key=lambda x: min(abstract_inv[x])))
    return work.get("abstract", "Аннотация отсутствует")


query1 = "ии в медицине"
# Пример использования:
articles = search_openalex(
    query1,
    per_page=3,
    #source_type="article",
    language="ru",
    sort_by='year'
)

# Теперь articles содержит список словарей с данными
"""for article in articles:
    print(f"Название: {article['title']}")
    print(f"Авторы: {', '.join(article['authors'])}")
    print(f"Год издания: {article['year']}")
    print(f"Аннотация: {article['abstract']}")
    print(f"Ссылка: {article['url']}")
    print('-'*80+'\n')"""

