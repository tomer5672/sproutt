from django.db import models


# Create your models here.
class Customer(models.Model):
    term = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    coverage = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.CharField(max_length=10)
    weight = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    health_class = models.CharField(max_length=20)
