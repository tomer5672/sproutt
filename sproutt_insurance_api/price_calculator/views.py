from rest_framework.response import Response
from rest_framework.views import APIView
from price_calculator.models import Customer, CalculatedResult, InsuranceDeclineException
from price_calculator.price_calculator_app import get_price_object
from django.http import JsonResponse
import logging

from price_calculator.seralizers import CustomerSerializer

logger = logging.getLogger(__name__)


class PriceViewSet(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(data={'error': 'Invalid input'}, status=400)
        term = int(request.data.get('term'))
        # calculate as int not double.
        coverage = int(request.data.get('coverage'))
        age = int(request.data.get('age'))
        height = request.data.get('height')
        weight = int(request.data.get('weight'))
        customer = Customer(term=term, coverage=coverage, age=age, height=height, weight=weight)
        try:
            calculated_result: CalculatedResult = get_price_object(customer=customer)
        except InsuranceDeclineException as decline_exception:
            return JsonResponse(data=decline_exception.to_dict(), status=400)
        except Exception as general_exception:
            logger.exception(general_exception)
            return JsonResponse(data={'error': 'Internal server error'}, status=500)

        result_dict = {'price': calculated_result.price,
                       'health-class': calculated_result.health_class,
                       'term': calculated_result.term,
                       'coverage': calculated_result.coverage
                       }
        logger.info(f'result_dict: {str(result_dict)}')
        return JsonResponse(data=result_dict, status=200)
