from django.db import models


# Create your models here.
class Customer(models.Model):
    term = models.PositiveIntegerField()
    age = models.PositiveIntegerField()
    coverage = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.TextField(max_length=10)
    weight = models.PositiveIntegerField()

    @property
    def tuple_height(self) -> tuple:
        # TODO
        height = str(self.height).replace(' ', '')
        feet, inches = height.split('ft')
        return int(feet), int(inches)


class CalculatedResult(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    health_class = models.TextField(max_length=10)
    term = models.PositiveIntegerField()
    coverage = models.DecimalField(max_digits=10, decimal_places=2)


class InsuranceDeclineException(Exception):
    def __init__(self, decline_message='insurance decline', *args):
        self.decline_message = decline_message
        super().__init__(*args)

    def to_dict(self):
        return {'insurance declined': self.decline_message}
