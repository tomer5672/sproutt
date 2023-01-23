from django.shortcuts import render
import pandas as pd
from sproutt_insurance_api.price_calculator.models import Customer
import os
from django.core.cache import cache
from numify.numify import numify
import re


def get_coverage_range(rates_table: pd.DataFrame, coverage_amount: int):
    regex = '\$\d+[kKmMbB]? - \$\d+[kKmMbB]?'
    range_list_str = set([col[0] for col in rates_table.columns if re.match(regex, col[0])])
    for range_str in range_list_str:
        low_limit, upper_limit = re.match('\$(\d+[kKmMbB]?) - \$(\d+[kKmMbB]?)', range_str).groups()
        if re.match('^([0-9]*)(\s)?([kKmMbB])$', low_limit):
            low_limit = numify(low_limit)
            low_limit -= 1
        else:
            low_limit = int(low_limit)
        if re.match('^([0-9]*)(\s)?([kKmMbB])$', upper_limit):
            number, letter = re.match('^([0-9]*)\s?([kKmMbB])$', upper_limit).groups()
            upper_limit = f'{int(number) + 1} {letter}'  # in order to include the numbers between each category.
            upper_limit = numify(upper_limit)
        else:
            upper_limit = int(upper_limit)
        if low_limit <= coverage_amount < upper_limit:
            return range_str
    return None


def get_max_column(row, weight):
    results = []
    for col in row.index:
        if weight > row[col]:
            results.append(col)
    if results:
        return results[-1]
    return None


def calculate_price(request):
    term = int(request.POST.get('term'))
    # calculate as int not double.
    coverage = int(request.POST.get('coverage'))
    age = int(request.POST.get('age'))
    height = request.POST.get('height')
    weight = request.POST.get('weight')

    customer = Customer(term=term, coverage=coverage, age=age, height=height, weight=weight)

    feet, inches = customer.tuple_height

    # TODO change the df names:
    health_class_df = get_file_as_df(file_path='Health Class table.xlsx', ordering_function=order_health_class_df,
                                     skiprows=3)
    rates_df = get_file_as_df(file_path='Rates-table.xlsx', header=[0, 1])

    relevant_row = health_class_df[(health_class_df['feet'] == feet) & (health_class_df['inches'] == inches)]
    relevant_row = relevant_row.drop(columns=['feet', 'inches'])
    health_class_series = relevant_row.apply(lambda row: get_max_column(row, 220), axis=1)
    if not health_class_series.empty:
        health_class = health_class_series.iloc[0]
        coverage_key = get_coverage_range(rates_table=rates_df, coverage_amount=int(coverage))
        if coverage_key:
            rate_row = rates_df[
                (rates_df['coverage']['age/health-class'] == age) & (rates_df['coverage']['term'] == term)]
            factor = rate_row[coverage_key][health_class]
            price = coverage / 1000 * factor
            # TODO continue
        else:
            pass
    else:
        pass


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
