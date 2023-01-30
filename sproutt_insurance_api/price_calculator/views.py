import logging
from rest_framework.views import APIView
from django.http import JsonResponse

from price_calculator.consts import INVALID_INPUT_MESSAGE
from price_calculator.models import Customer, CalculatedResult, InsuranceDeclineException
from price_calculator.price_calculator_app import get_price_object
from price_calculator.seralizers import CustomerSerializer

logger = logging.getLogger(__name__)


class PriceView(APIView):
    http_method_names = ['post']

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        logger.info(f'input: {str(request.data)}')
        if not serializer.is_valid():
            return JsonResponse(data=INVALID_INPUT_MESSAGE, status=400)
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
            logger.info(f'insurance decline: {str(decline_exception.to_dict())}')
            return JsonResponse(data=decline_exception.to_dict(), status=400)
        except Exception as general_exception:
            logger.exception(f"Unexpected error: {general_exception}")
            return JsonResponse(data={'error': 'Internal server error'}, status=500)
        result_dict = calculated_result.to_dict()
        logger.info(f'result: {str(result_dict)}')
        return JsonResponse(data=result_dict, status=200)
