from django.urls import reverse
from django.test import Client
from rest_framework.test import APITestCase


class CreateUrlTest(APITestCase):

    def setUp(self):
        """
        Set up test data for the test cases.
        """
        self.costume_client = Client(HTTP_HOST='localhost')
        self.insurance_data = {
            "term": 10,
            "coverage": 250000,
            "age": 25,
            "height": "5 ft 1",
            "weight": 160
        }

    def test_price_calculate(self):
        expected_response_data = {
            "price": 107.275,
            "health-class": "Preferred",
            "term": 10,
            "coverage": 250000
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response_data)

    def test_overweight_calculate(self):
        self.insurance_data['weight'] = 500
        expected_response_data = {
            "insurance declined": "weight is too high"
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_underweight_calculate(self):
        self.insurance_data['weight'] = 50
        expected_response_data = {
            "insurance declined": "weight is too low"
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_coverage_calculate(self):
        self.insurance_data['coverage'] = 5000
        expected_response_data = {
            "insurance declined": "coverage amount illegal"
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)
