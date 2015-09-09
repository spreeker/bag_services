from rest_framework.test import APITestCase
import datasets.bag.batch
from batch import batch


class QueryTest(APITestCase):

    fixtures = ['dataset.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        batch.execute(datasets.bag.batch.IndexJob())

    def test_non_matching_query(self):
        response = self.client.get('/api/search/', dict(q="anjel"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hits', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 0)

    def test_matching_query(self):
        response = self.client.get('/api/search/', dict(q="anjel*"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('hits', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 4)
