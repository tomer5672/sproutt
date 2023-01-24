import pandas as pd
from price_calculator.models import Customer, CalculatedResult,InsuranceDeclineException
from os.path import dirname, join, getmtime, splitext, basename
from django.core.cache import cache
from numify.numify import numify
import re


def get_price_object(customer:Customer):
    feet, inches = customer.tuple_height
    files_dir = join(dirname(__file__), 'files')
    health_class_df = get_file_as_df(file_path=join(files_dir, 'Health Class table.xlsx'),
                                     ordering_function=order_health_class_df,
                                     skiprows=3)
    rates_df = get_file_as_df(file_path=join(files_dir, 'Rates-table.xlsx'), header=[0, 1])
    relevant_row = health_class_df[(health_class_df['feet'] == feet) & (health_class_df['inches'] == inches)]
    relevant_row = relevant_row.drop(columns=['feet', 'inches'])
    health_class_series = relevant_row.apply(lambda row: get_max_column(row, customer.weight), axis=1)
    health_class = health_class_series.iloc[0]
    if health_class == 'Declined':
        raise InsuranceDeclineException('weight is too high')
    if health_class == 'Declined_lower_limit':
        raise InsuranceDeclineException('weight is too low')
    coverage_key = get_coverage_range(rates_table=rates_df, coverage_amount=customer.coverage)
    if coverage_key:
        rate_row = rates_df[
            (rates_df['coverage']['age/health-class'] == customer.age) & (
                    rates_df['coverage']['term'] == customer.term)]
        factor = rate_row[coverage_key][health_class].iloc[0]
        price = round(customer.coverage / 1000 * factor, 3)

        result = CalculatedResult(price=price, health_class=health_class, term=customer.term, coverage=customer.coverage)
    else:
        raise InsuranceDeclineException('coverage amount illegal')
    return result


def get_coverage_range(rates_table: pd.DataFrame, coverage_amount: int):
    regex = '\$\d+[kKmMbB]? - \$\d+[kKmMbB]?'
    range_list_str = set([col[0] for col in rates_table.columns if re.match(regex, col[0])])
    for range_str in range_list_str:
        low_limit_str, upper_limit_str = re.match('\$(\d+[kKmMbB]?) - \$(\d+[kKmMbB]?)', range_str).groups()
        if re.match('^([0-9]*)(\s)?([kKmMbB])$', low_limit_str):
            low_limit = numify(low_limit_str)
            low_limit -= 1
        else:
            low_limit = int(low_limit_str)
        if re.match('^([0-9]*)(\s)?([kKmMbB])$', upper_limit_str):
            number, letter = re.match('^([0-9]*)\s?([kKmMbB])$', upper_limit_str).groups()
            upper_limit_str = f'{int(number) + 1} {letter}'  # in order to include the numbers between each category.
            upper_limit = numify(upper_limit_str)
        else:
            upper_limit = int(upper_limit_str)
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
    return 'Declined_lower_limit'


def get_file_as_df(file_path, ordering_function: callable = lambda *args: None, **kwargs):
    file_modified_timestamp = getmtime(file_path)
    file_name = splitext(basename(file_path))[0]
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
