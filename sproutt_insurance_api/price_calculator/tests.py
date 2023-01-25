from django.urls import reverse
from django.test import Client
from rest_framework.test import APITestCase

from price_calculator.consts import COVERAGE_ILLEGAL_MESSAGE, LOW_WEIGHT_MESSAGE, HIGH_WEIGHT_MESSAGE, \
    ILLEGAL_HEIGHT_MESSAGE, ILLEGAL_AGE_MESSAGE, ILLEGAL_TERM_MESSAGE, INVALID_INPUT_MESSAGE


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

    def test_overweight(self):
        self.insurance_data['weight'] = 500
        expected_response_data = {
            "insurance declined": HIGH_WEIGHT_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_underweight(self):
        self.insurance_data['weight'] = 50
        expected_response_data = {
            "insurance declined": LOW_WEIGHT_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_coverage(self):
        self.insurance_data['coverage'] = 5000
        expected_response_data = {
            "insurance declined": COVERAGE_ILLEGAL_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_height(self):
        self.insurance_data['height'] = '7 ft 0'
        expected_response_data = {
            "insurance declined": ILLEGAL_HEIGHT_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_age(self):
        self.insurance_data['age'] = 2
        expected_response_data = {
            "insurance declined": ILLEGAL_AGE_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_term(self):
        self.insurance_data['term'] = 2
        expected_response_data = {
            "insurance declined": ILLEGAL_TERM_MESSAGE
        }
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)

    def test_incorrect_input_format(self):
        self.insurance_data['term'] = 'str'
        expected_response_data = INVALID_INPUT_MESSAGE
        response = self.costume_client.post(reverse('url-calculate'), data=self.insurance_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), expected_response_data)