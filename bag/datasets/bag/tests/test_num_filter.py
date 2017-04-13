# Python
import logging
# Packages
from django.contrib.gis.geos import Point
from rest_framework.test import APITestCase

from datasets.bag.tests import factories as bag_factories
from datasets.brk.tests import factories as brk_factories

LOG = logging.getLogger(__name__)


class Numfilter(APITestCase):

    def setUp(self):

        self.num = bag_factories.NummeraanduidingFactory.create(
            postcode='1000AN'  # default postcode..
        )

        self.vbo = bag_factories.VerblijfsobjectFactory.create(
            geometrie=Point(1000, 1000, srid=28992))

        self.ligplaats = bag_factories.LigplaatsFactory.create()

        self.num_ligplaats = bag_factories.NummeraanduidingFactory.create(
            postcode='1233AN',
            ligplaats=self.ligplaats
        )

        self.standplaats = bag_factories.StandplaatsFactory.create()

        self.num_standplaats = bag_factories.NummeraanduidingFactory.create(
            postcode='1233XX',
            standplaats=self.standplaats
        )

        self.pand = bag_factories.PandFactory.create()
        self.pand_vbo = bag_factories.VerblijfsobjectPandRelatie.create(
            pand=self.pand,
            verblijfsobject=self.vbo)

        self.kot = brk_factories.KadastraalObjectFactory()

        self.kot_vbo = (
            brk_factories.KadastraalObjectVerblijfsobjectRelatieFactory
            .create(
                kadastraal_object=self.kot,
                verblijfsobject=self.vbo
            )
         )

        # add adres to vbo
        self.vbo.adressen.add(self.num)

        # Creating an extra Nummeraanduiding.
        # this should be expanded to a full item
        self.bad_na = bag_factories.NummeraanduidingFactory.create(
            postcode='2000ZZ')

    def test_kot_filter(self):
        url = f'/bag/nummeraanduiding/?kadastraalobject={self.kot.id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_pand_filter(self):
        url = f'/bag/nummeraanduiding/?pand={self.pand.landelijk_id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_vbo_filter(self):
        url = f'/bag/nummeraanduiding/?verblijfsobject={self.vbo.landelijk_id}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_standplaats_filter(self):
        test_param = f"standplaats={self.standplaats.landelijk_id}"
        url = f'/bag/nummeraanduiding/?{test_param}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num_standplaats.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_ligplaats_filter(self):
        test_param = f"ligplaats={self.ligplaats.landelijk_id}"
        url = f'/bag/nummeraanduiding/?{test_param}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()

        self.assertEquals(
            self.num_ligplaats.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.num.postcode}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_partial_postcode_filter(self):
        url = f'/bag/nummeraanduiding/?postcode={self.num.postcode[:4]}'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])
        self.assertEquals(
            len(data['results']), 1
        )

    def test_openbare_ruimte_filter(self):
        url = f'/bag/nummeraanduiding/?openbare_ruimte={self.num.openbare_ruimte.naam[:5]}'   # noqa
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_location_filter(self):
        url = '/bag/nummeraanduiding/?locatie=1000,1000,10'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        self.assertEquals(
            self.num.landelijk_id,
            data['results'][0]['landelijk_id'])

    def test_detailed_view(self):
        url = '/bag/nummeraanduiding/?detailed=1'
        response = self.client.get(url)

        self.assertEquals(200, response.status_code)
        data = response.json()
        # Making sure the details in response contains the detailed fields
        detailed = len(data['results'][0].keys()) > 14
        self.assertEquals(detailed, True)
