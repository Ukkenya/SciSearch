from django.shortcuts import render
from .openalex import search_openalex
from .rus_model import rus

def index(request):
    # получаем данные запросов GET
    years = list(range(2025, 1939, -1))
    type = request.GET.get('type')
    sel_year_one = request.GET.get('year-one')
    sel_year_two = request.GET.get('year-two')
    lang = request.GET.get('lang', '')
    sort = request.GET.get('select-sort', '')
    search_input = request.GET.get('search_input', '')

    # если года публикации от и до заданы в обратном порядке, то меняем их местами
    if sel_year_one and sel_year_two and sel_year_one!='all' and sel_year_two!='all' and sel_year_two<sel_year_one:
        sel_year_two, sel_year_one = sel_year_one, sel_year_two

    int_sel_year_one = int(sel_year_one) if sel_year_one and sel_year_one != 'all' else None
    int_sel_year_two = int(sel_year_two) if sel_year_two and sel_year_two != 'all' else None

    articles = []

    if search_input:
        if lang == "en":
            type_openalex = {
                'dissert': 'dissertation',
                'stat': 'article',
                'conf': None,
                'book': 'book',
                'all': None,
            }
            from_year = None
            to_year = None
            if sel_year_one and sel_year_one != 'all':
                try:
                    from_year = int(sel_year_one)
                except ValueError:
                    pass
            if sel_year_two and sel_year_two != 'all':
                try:
                    to_year = int(sel_year_two)
                except ValueError:
                    pass
            articles = search_openalex(
                search_input + ' conference' if type == 'conf' else search_input,
                per_page=50,
                language="en",
                from_year=from_year,
                to_year=to_year,
                source_type=type_openalex[type] if type else None,
                sort_by=sort if sort else None
            )
            for article in articles:
                article['authors'] = ', '.join(article['authors']) if article['authors'] else 'не указаны'

        elif lang == 'ru':
            articles = rus(
                query=search_input,
                from_year=sel_year_one if sel_year_one != 'all' else None,
                to_year=sel_year_two if sel_year_two != 'all' else None,
                sort_by=sort,
                obj_type=type
            )

    else:
        articles = []
    return render(request, 'myapp/index.html', {
        "articles": articles,
        "years": years,
        "sel_year_one": int_sel_year_one,
        "sel_year_two": int_sel_year_two,
        "type": type,
        "lang": lang,
        "sort": sort,
        "search_input": search_input,
    })

