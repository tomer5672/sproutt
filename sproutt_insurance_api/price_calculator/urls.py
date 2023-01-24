# basic URL Configurations
from django.urls import include, path
from price_calculator.views import PriceViewSet

# specify URL Path for rest_framework
urlpatterns = [
    path('price/', PriceViewSet.as_view(),name='url-calculate'),
]