from django.urls import path
from price_calculator.views import PriceView


urlpatterns = [
    path('price/', PriceView.as_view(), name='url-calculate'),
]
