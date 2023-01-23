# basic URL Configurations
from django.urls import include, path
# import routers
from rest_framework import routers

# import everything from views
from price_calculator.views import PriceViewSet

# define the router
#router = routers.DefaultRouter()

# define the router path and viewset to be used
#router.register(r'price', PriceViewSet)

# specify URL Path for rest_framework
urlpatterns = [
    #path('', include(router.urls)),
    path('price/', PriceViewSet.as_view()),
]