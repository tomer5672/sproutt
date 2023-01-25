import os
import pandas
from os.path import dirname, join, getmtime, splitext, basename
from numify.numify import numify
import re
from dotenv import load_dotenv
from django.core.cache import cache
from price_calculator.consts import FEET_KEY, INCHES_KEY, DECLINED_LOW_WEIGHT, LAST_MODIFIED_CACHE_KEY, \
    LOW_WEIGHT_MESSAGE, HIGH_WEIGHT_MESSAGE, COVERAGE_ILLEGAL_MESSAGE, RANGE_FIELD_REGEX, LIMIT_REGEX, \
    ILLEGAL_AGE_MESSAGE, ILLEGAL_TERM_MESSAGE, ILLEGAL_COMBINATION_MESSAGE, ILLEGAL_HEIGHT_MESSAGE, DECLINED_STATUS
from price_calculator.models import Customer, CalculatedResult, InsuranceDeclineException

load_dotenv()


def get_price_object(customer: Customer):
    feet, inches = customer.tuple_height
    files_dir = join(dirname(__file__), 'files')
    health_class_df = get_file_as_df(file_path=join(files_dir, os.environ.get('HEALTH_CLASS_TABLE_FILE')),
                                     ordering_function=order_health_class_df,
                                     skiprows=3)
    rates_df = get_file_as_df(file_path=join(files_dir, os.environ.get('RATES_TABLE_FILE')), header=[0, 1])
    height_row = get_height_row(health_class_df=health_class_df, feet=feet, inches=inches)
    health_class_series = height_row.apply(lambda row: get_weight_max_column(row, customer.weight), axis=1)
    health_class = health_class_series.iloc[0]
    if health_class == DECLINED_STATUS:
        raise InsuranceDeclineException(HIGH_WEIGHT_MESSAGE)
    if health_class == DECLINED_LOW_WEIGHT:
        raise InsuranceDeclineException(LOW_WEIGHT_MESSAGE)
    coverage_key = get_coverage_range(rates_table=rates_df, coverage_amount=customer.coverage)
    if coverage_key:
        rate_row = get_rate_row(rates_df=rates_df, age=customer.age, term=customer.term)
        factor = rate_row[coverage_key][health_class].iloc[0]
        price = round(customer.coverage / 1000 * factor, 3)

        result = CalculatedResult(price=price, health_class=health_class, term=customer.term,
                                  coverage=customer.coverage)
    else:
        raise InsuranceDeclineException(COVERAGE_ILLEGAL_MESSAGE)
    return result


def get_coverage_range(rates_table: pandas.DataFrame, coverage_amount: int) -> str:
    # find the right range for input coverage.
    range_list_str = set(
        [(col[0], re.match(RANGE_FIELD_REGEX, col[0])) for col in rates_table.columns if
         re.match(RANGE_FIELD_REGEX, col[0])])
    for range_str, matching_object in range_list_str:
        low_limit_str, upper_limit_str = matching_object.groups()
        matching_low_limit_str = re.match(LIMIT_REGEX, low_limit_str)
        if matching_low_limit_str:
            low_limit = numify(low_limit_str)
            low_limit -= 1
        else:
            low_limit = int(low_limit_str)
        matching_upper_limit_str = re.match(LIMIT_REGEX, upper_limit_str)
        if matching_upper_limit_str:
            number, letter = matching_upper_limit_str.groups()
            upper_limit_str = f'{int(number) + 1} {letter}'  # in order to include the numbers between each category.
            upper_limit = numify(upper_limit_str)
        else:
            upper_limit = int(upper_limit_str)
        if low_limit <= coverage_amount < upper_limit:
            return range_str
    return None


def get_weight_max_column(row, weight) -> str:
    results = []
    for col in row.index:
        if weight > row[col]:
            results.append(col)
    if results:
        return results[-1]
    return DECLINED_LOW_WEIGHT


def get_file_as_df(file_path: str, ordering_function: callable = lambda *args: None, **kwargs):
    # get file using cache
    file_modified_timestamp = getmtime(file_path)
    file_name = splitext(basename(file_path))[0]
    data_file = cache.get(file_name)
    last_modified_timestamp_key = f'{file_name}_{LAST_MODIFIED_CACHE_KEY}'
    last_modified_timestamp = cache.get(last_modified_timestamp_key)
    if last_modified_timestamp is None or last_modified_timestamp != file_modified_timestamp or data_file is None:
        data_file: pandas.DataFrame = pandas.read_excel(file_path, **kwargs)
        ordering_function(data_file)
        cache.set(file_name, data_file)
        cache.set(last_modified_timestamp_key, file_modified_timestamp)
    return data_file


def order_health_class_df(health_class_df: pandas.DataFrame) -> None:
    # drop the first line because it is not a relevant data.
    # parse height as feet and inches integers.
    mapping = {health_class_df.columns[0]: FEET_KEY, health_class_df.columns[1]: INCHES_KEY}
    health_class_df.rename(columns=mapping, inplace=True)
    health_class_df.drop(0, inplace=True)
    health_class_df.reset_index(drop=True, inplace=True)
    health_class_df[FEET_KEY] = health_class_df[FEET_KEY].replace(to_replace='[\'|’]', value='', regex=True)
    health_class_df[FEET_KEY] = health_class_df[FEET_KEY].astype(int)
    health_class_df[INCHES_KEY] = health_class_df[INCHES_KEY].replace(to_replace='[\"|”]', value='', regex=True)
    health_class_df[INCHES_KEY] = health_class_df[INCHES_KEY].astype(int)


def get_rate_row(rates_df: pandas.DataFrame, age: int, term: int):
    rate_row = rates_df[
        (rates_df['coverage']['age/health-class'] == age) & (
                rates_df['coverage']['term'] == term)]
    if rate_row.empty:
        if rates_df[(rates_df['coverage']['age/health-class'] == age)].empty:
            raise InsuranceDeclineException(ILLEGAL_AGE_MESSAGE)
        elif rates_df[(rates_df['coverage']['term'] == term)].empty:
            raise InsuranceDeclineException(ILLEGAL_TERM_MESSAGE)
        else:
            raise InsuranceDeclineException(ILLEGAL_COMBINATION_MESSAGE)
    return rate_row


def get_height_row(health_class_df: pandas.DataFrame, feet: int, inches: int):
    height_row = health_class_df[(health_class_df[FEET_KEY] == feet) & (health_class_df[INCHES_KEY] == inches)]
    if height_row.empty:
        raise InsuranceDeclineException(ILLEGAL_HEIGHT_MESSAGE)
    return height_row.drop(columns=[FEET_KEY, INCHES_KEY])
