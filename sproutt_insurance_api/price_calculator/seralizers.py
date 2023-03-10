from price_calculator.models import Customer
from rest_framework import serializers


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('term', 'age', 'coverage', 'height', 'weight')