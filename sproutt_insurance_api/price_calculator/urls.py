from django.urls import path
from price_calculator.views import PriceViewSet


urlpatterns = [
    path('price/', PriceViewSet.as_view(), name='url-calculate'),
]
