from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("price_calculator.urls"))
]
