
import unittest

from rest_framework.test import APITestCase

import datasets.bag.batch
from datasets.bag.tests import factories as bag_factories

# from datasets.brk.tests import factories as brk_factories


import datasets.brk.batch
from batch import batch


class AanduidingenSearchTest(APITestCase):

    @classmethod
    def setUpClass(cls):

        super().setUpClass()

        ptt_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Marius Cornelis straat",
            naam_ptt="M Cornelisstr",
            type='01')

        nen_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Stoom Maker Weg",
            naam_nen="S Maker wg",
            type='01')

        straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Anjeliersstraat", type='01')

        gracht = bag_factories.OpenbareRuimteFactory.create(
            naam="Prinsengracht", type='01')

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=192,
            huisletter='A',
            type='01',  # Verblijfsobject
            openbare_ruimte=gracht
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=42,
            huisletter='F',
            type='01',  # Verblijfsobject
            openbare_ruimte=straat
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=99,
            huisletter='',
            type='01',  # Verblijfsobject
            openbare_ruimte=ptt_straat
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=100,
            huisletter='',
            type='01',  # Verblijfsobject
            openbare_ruimte=nen_straat
        )

        metro_station_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Metrostation Weesperplein",
            type='01')

        metro_straat = bag_factories.OpenbareRuimteFactory.create(
            naam="Weesperplein",
            type='01')

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=1,
            huisletter='',
            type='01',  # Verblijfsobject
            openbare_ruimte=metro_station_straat
        )

        bag_factories.NummeraanduidingFactory.create(
            huisnummer=1,
            huisletter='',
            type='01',  # Verblijfsobject
            openbare_ruimte=metro_straat
        )

        batch.execute(datasets.bag.batch.IndexBagJob())
        batch.execute(datasets.brk.batch.IndexKadasterJob())

    def test_straat_query(self):
        response = self.client.get(
            '/atlas/search/adres/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        self.assertEqual(response.data['count'], 1)

        first = response.data['results'][0]
        self.assertEqual(first['straatnaam'], "Anjeliersstraat")

    def test_gracht_query(self):
        response = self.client.get(
            "/atlas/search/adres/", dict(q="prinsengracht 192"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)

        self.assertEqual(
            response.data['results'][0]['adres'], "Prinsengracht 192A")

    @unittest.skip("fix this later!")
    def test_nen_query(self):
        response = self.client.get(
            "/atlas/search/adres/", dict(q="s maker wg"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 1)

        self.assertEqual(
            response.data['results'][0]['adres'], "Stoom Maker Weg 100")

    def test_ptt_query(self):
        response = self.client.get(
            "/atlas/search/adres/", dict(q="M Cornelisstr"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        # self.assertEqual(response.data['count'], 1)
        results = str(response.data['results'][:3])

        self.assertIn(
            "Marius Cornelis straat 99", results)

    def test_straat_volgorde(self):
        response = self.client.get(
            "/atlas/search/adres/", dict(q="Weesperplein"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 2)

        score_1 = response.data['results'][0]['score']
        score_2 = response.data['results'][1]['score']

        # it is possible to mess up oder-ing
        self.assertTrue(score_1 > score_2)

        self.assertEqual(
            response.data['results'][0]['adres'], "Weesperplein 1")

        self.assertEqual(
            response.data['results'][1]['adres'],
            "Metrostation Weesperplein 1")

    def test_gracht_dash_query(self):
        response = self.client.get(
            "/atlas/search/adres/", dict(q="prinsengracht 192-A"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        # self.assertEqual(response.data['count'], 1)
        result = str(response.data['results'][:3])

        self.assertIn("Prinsengracht 192A", result)
