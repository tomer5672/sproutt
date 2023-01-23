from sproutt_insurance_api.price_calculator.models import Customer
from rest_framework import serializers


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ['term', 'age', 'coverage', 'height', 'weight']