# Create your views here.
from collections import OrderedDict
import re

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch.exceptions import TransportError
from rest_framework import viewsets, metadata
from rest_framework.response import Response
from rest_framework.reverse import reverse

from datasets.generic import rest

_details = {
    'ligplaats': 'ligplaats-detail',
    'standplaats': 'standplaats-detail',
    'verblijfsobject': 'verblijfsobject-detail',
    'openbare_ruimte': 'openbareruimte-detail',
    'kadastraal_subject': 'kadastraalsubject-detail',
    'kadastraal_object': 'kadastraalobject-detail',
}

all_autocomplete_fields = [
    "openbare_ruimte.naam",
    "openbare_ruimte.postcode",
    "ligplaats.adres",
    "standplaats.adres",
    "verblijfsobject.adres",
    "kadastraal_subject.geslachtsnaam",
    "kadastraal_subject.naam",
    "kadastraal_object.aanduiding",
]

all_fuzzy_autocomplete_fields = [
    "openbare_ruimte.naam",
    "kadastraal_subject.geslachtsnaam"
]

all_autocomplete_docs = list(
        set([doc.split('.')[0] for doc in all_autocomplete_fields + all_fuzzy_autocomplete_fields])
)


def _get_url(request, doc_type, id):
    if doc_type in _details:
        return rest.get_links(view_name=_details[doc_type], kwargs=dict(pk=id), request=request)

    return None


class QueryMetadata(metadata.SimpleMetadata):
    def determine_metadata(self, request, view):
        result = super().determine_metadata(request, view)
        result['parameters'] = dict(
            q=dict(
                type="string",
                description="The query to search for",
                required=False
            )
        )
        return result


def cleanup_query(query):
    regex_partial = [
        re.compile(r'[a-zA-Z]+\s+(\d+\s+\w)$'),  # straat huisnummer huisletter
        re.compile(r'[a-zA-Z]+\s+(\d+\s+(?:\w)?-\w{1,4})$')  # straat huisnummer huisletter toevoeging
    ]

    regex_exact = [
        re.compile(r'^(\d{4}\s+[a-zA-Z]{2,})$'),  # postcode
        re.compile(r'^(\d{4}\s+[a-zA-Z]{2})\s+(\d+)$'),  # postcode huisnummer
        re.compile(r'^(\d{4}\s?[a-zA-Z]{2,})\s+(\d+\s+\w)$'),  # postcode huisnummer huisletter
        re.compile(r'^(\d{4}\s?[a-zA-Z]{2})\s+(\d+(?:\s\w)?-\w{1,4})$')  # postcode huisnummer huisletter? toevoeging
    ]

    # first exact matches
    for regex in regex_exact:
        m = regex.search(query)
        if m:
            result = [match.replace(' ', '') for match in m.groups()]
            return ' '.join(result)

    # partial matches
    for regex in regex_partial:
        m = regex.search(query)
        if m:
            return query.replace(m.groups()[0], m.groups()[0].replace(' ', ''))

    return query


def search_query(client, query):
    query = cleanup_query(query)
    wildcard = '*{}*'.format(query)

    return (
        Search(client)
            .index('bag', 'brk')
            .query(Q("multi_match", type="phrase_prefix", query=query,
                     fields=['naam', 'adres', 'postcode', 'geslachtsnaam', 'aanduiding'])
                   | Q("wildcard", naam=dict(value=wildcard))
                   )
            .sort({"order": {"order": "asc", "missing": "_last", "unmapped_type": "long"}},
                  {"straatnaam": {"order": "asc", "missing": "_first", "unmapped_type": "string"}},
                  {"huisnummer": {"order": "asc", "missing": "_first", "unmapped_type": "long"}},
                  {"adres": {"order": "asc", "missing": "_first", "unmapped_type": "string"}},
                  '-_score',
                  'naam',
                  )
    )


def autocomplete_query(client, document, query):
    query = cleanup_query(query)

    match_fields = [d for d in all_autocomplete_fields if document in d]
    fuzzy_fields = [d for d in all_fuzzy_autocomplete_fields if document in d]

    completions = [
        "naam",
        "adres",
        "postcode",
        "geslachtsnaam",
        "aanduiding",
    ]

    q = Q("multi_match", query=query, type="phrase_prefix", fields=match_fields)
    if len(fuzzy_fields):
        q |= Q("multi_match", query=query, fuzziness="auto", prefix_length=1, fields=fuzzy_fields)

    return (
        Search(client)
            .index('bag', 'brk')
            .query(q)
            .highlight(*completions, pre_tags=[''], post_tags=[''])
    )


def get_autocomplete_response(client, query):
    matches = dict()

    # execute query per document to distribute the results across all documents
    for doc_type in all_autocomplete_docs:
        doc_matches = OrderedDict()

        for r in autocomplete_query(client, doc_type, query)[0:5].execute():
            h = r.meta.highlight
            for key in h:
                highlights = h[key]
                for match in highlights:
                    doc_matches[match] = 1

        keys = doc_matches.keys()

        if len(keys):
            matches[doc_type.replace('_', ' ')] = [dict(item=m) for m in keys]

    return matches


class TypeaheadViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all objects that (partially) match the
    specified query.
    """

    metadata_class = QueryMetadata

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        query = request.query_params['q']

        response = get_autocomplete_response(self.client, query)
        return Response(response)


class SearchViewSet(viewsets.ViewSet):
    """
    Given a query parameter `q`, this function returns a subset of all object that match the elastic search query.
    """

    metadata_class = QueryMetadata
    page_size = 100

    def list(self, request, *args, **kwargs):
        if 'q' not in request.query_params:
            return Response([])

        page = 1
        if 'page' in request.query_params:
            page = int(request.query_params['page'])

        start = ((page - 1) * self.page_size)
        end = (page * self.page_size)

        query = request.query_params['q']

        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        search = search_query(client, query)[start:end]

        try:
            result = search.execute()
        except TransportError:
            # Todo fix this https://github.com/elastic/elasticsearch/issues/11340#issuecomment-105433439
            return Response([])

        followup_url = reverse('search-list', request=request)
        if page == 1:
            prev_page = None
        elif page == 2:
            prev_page = "{}?q={}".format(followup_url, query)
        else:
            prev_page = "{}?q={}&page={}".format(followup_url, query, page - 1)

        total = result.hits.total
        if end >= total:
            next_page = None
        else:
            next_page = "{}?q={}&page={}".format(followup_url, query, page + 1)

        res = OrderedDict()
        res['_links'] = OrderedDict([
            ('self', dict(href=followup_url)),
        ])
        if next_page:
            res['_links']['next'] = dict(href=next_page)
        else:
            res['_links']['next'] = None

        if prev_page:
            res['_links']['previous'] = dict(href=prev_page)
        else:
            res['_links']['previous'] = None

        res['count'] = result.hits.total
        res['results'] = [self.normalize_hit(h, request) for h in result.hits]

        return Response(res)

    def normalize_hit(self, hit, request):
        result = OrderedDict()
        result['_links'] = _get_url(request, hit.meta.doc_type, hit.meta.id)
        result['type'] = hit.meta.doc_type
        result['dataset'] = hit.meta.index
        # result['uri'] = _get_url(request, hit.meta.doc_type, hit.meta.id) + "?full"
        result.update(hit.to_dict())

        return result
