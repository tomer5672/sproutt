from django.shortcuts import render
import pandas as pd
from sproutt_insurance_api.price_calculator.models import Customer
import os
from django.core.cache import cache


def calculate_price(request):
    term = request.POST.get('term')
    coverage = request.POST.get('coverage')
    age = request.POST.get('age')
    height = request.POST.get('height')
    weight = request.POST.get('weight')


    #TODO change the df names:
    df1 = get_file_as_df('Health Class table.xlsx')
    df2 = get_file_as_df('Rates-table.xlsx')
    factor = df1[df1['term'] == term]['factor'].values[0]
    health_class = df2[df2['age'] == age]['health_class'].values[0]
    # Calculate the price
    price = coverage / 1000 * factor

    # Create the quote object
    quote = Customer(term=term, coverage=coverage, age=age, height=height, weight=weight, price=price,
                     health_class=health_class)


def get_file_as_df(file_path):
    file_modified_timestamp = os.path.getmtime(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))
    data_file = cache.get(f'{file_name}{str(file_modified_timestamp)}')
    if data_file is None:
        data_file = pd.read_excel(file_path)
        cache.set(f'{file_name}{str(file_modified_timestamp)}', data_file)
    return data_file
