from django.shortcuts import render
import pandas as pd
from sproutt_insurance_api.price_calculator.models import Customer
import os
from django.core.cache import cache,lock


def calculate_price(request):
    term = request.POST.get('term')
    coverage = request.POST.get('coverage')
    age = request.POST.get('age')
    height = request.POST.get('height')
    weight = request.POST.get('weight')

    # TODO change the df names:
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
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    data_file = cache.get(f'{file_name}{str(file_modified_timestamp)}')
    last_modified_timestamp_key = f'{file_name}_last_modified'
    last_modified_timestamp = cache.get(last_modified_timestamp_key)
    if last_modified_timestamp is None or last_modified_timestamp != file_modified_timestamp or data_file is None:
        lock_key = f'{file_name}_lock'
        # Acquire the lock before reading the file
        with lock(lock_key):
            data_file = pd.read_excel(file_path)
            cache.set(file_name, data_file)
            cache.set(last_modified_timestamp_key, file_modified_timestamp)
    return data_file
