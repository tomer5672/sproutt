from django.shortcuts import render
import pandas as pd
from sproutt_insurance_api.price_calculator.models import Customer
import os
from django.core.cache import cache


def get_max_column(row, weight):
    results = []
    for col in row.index:
        if weight > row[col]:
            results.append(col)
    if results:
        return results[-1]
    return None

def calculate_price(request):
    term = request.POST.get('term')
    coverage = request.POST.get('coverage')
    age = request.POST.get('age')
    height = request.POST.get('height')
    weight = request.POST.get('weight')

    customer = Customer(term=term, coverage=coverage, age=age, height=height, weight=weight)

    feet, inches = customer.tuple_height

    # TODO change the df names:
    df1 = get_file_as_df(file_path='Health Class table.xlsx', ordering_function=order_health_class_df, skiprows=3)
    df2 = get_file_as_df(file_path='Rates-table.xlsx', header=[0, 1])

    relevant_row = df1[(df1['feet'] == feet) & (df1['inches'] == inches)]
    relevant_row = relevant_row.drop(columns=['feet', 'inches'])
    health_class_series = relevant_row.apply(lambda row: get_max_column(row, 220), axis=1)
    if health_class_series:
        health_class = health_class_series.iloc[0]

    health_class = df1[df1['term'] == term]['factor'].values[0]
    # health_class = df2[df2['age'] == age]['health_class'].values[0]
    # Calculate the price
    # price = coverage / 1000 * factor

    # Create the quote object
    # quote = Customer(term=term, coverage=coverage, age=age, height=height, weight=weight, price=price,
    #                  health_class=health_class)


def get_file_as_df(file_path, ordering_function: callable = lambda *args: None, **kwargs):
    file_modified_timestamp = os.path.getmtime(file_path)
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    data_file = cache.get(file_name)
    last_modified_timestamp_key = f'{file_name}_last_modified'
    last_modified_timestamp = cache.get(last_modified_timestamp_key)
    if last_modified_timestamp is None or last_modified_timestamp != file_modified_timestamp or data_file is None:
        # Acquire the lock before reading the file
        data_file: pd.DataFrame = pd.read_excel(file_path, **kwargs)
        ordering_function(data_file)
        cache.set(file_name, data_file)
        cache.set(last_modified_timestamp_key, file_modified_timestamp)
    return data_file


def order_health_class_df(health_class_df: pd.DataFrame):
    mapping = {health_class_df.columns[0]: 'feet', health_class_df.columns[1]: 'inches'}
    health_class_df.rename(columns=mapping, inplace=True)
    health_class_df.drop(0, inplace=True)
    health_class_df.reset_index(drop=True, inplace=True)
    health_class_df['feet'] = health_class_df['feet'].replace(to_replace='[\'|’]', value='', regex=True)
    health_class_df['feet'] = health_class_df['feet'].astype(int)
    health_class_df['inches'] = health_class_df['inches'].replace(to_replace='[\"|”]', value='', regex=True)
    health_class_df['inches'] = health_class_df['inches'].astype(int)
