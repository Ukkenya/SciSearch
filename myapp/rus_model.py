from .nab import parse_neb
from .scholar import parse_scholar


def rus(query, from_year=None, to_year=None, sort_by=None, obj_type='all'):
    if obj_type=='dissert':
        results = parse_neb(query, from_year=from_year, to_year=to_year, sort_by=sort_by)

    elif obj_type!='dissert' and obj_type!='all':
        if obj_type=='stat': query = "статья "+query
        if obj_type=='conf': query = "материалы конференции "+query
        if obj_type=='book': query = "книги "+query

        results = parse_scholar(query, from_year=from_year, to_year=to_year, sort_by=sort_by)
    elif obj_type=='all':
        results_nab = parse_neb(query, from_year=from_year, to_year=to_year)
        results_scholar = parse_scholar(query, from_year=from_year, to_year=to_year)

        results = results_nab + results_scholar
        if sort_by == 'author':
            # Сортировка по автору (по алфавиту)
            results = sorted(results, key=lambda x: x['authors'])
        if sort_by == 'year':
            # Сортировка по году (сначала свежее)
            results = sorted(results, key=lambda x: x['year'], reverse=True)

    return results
