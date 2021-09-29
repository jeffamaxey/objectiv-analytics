"""
Copyright 2021 Objectiv B.V.
"""
import datetime

import numpy as np

from buhtuh import BuhTuhSeriesInt64, BuhTuhSeriesString, BuhTuhSeriesFloat64, BuhTuhSeriesBoolean, \
    BuhTuhSeriesDate, BuhTuhSeriesTimestamp, BuhTuhSeriesTime, BuhTuhSeriesTimedelta
from tests.functional.buhtuh.test_data_and_utils import get_bt_with_test_data, check_expected_db_type, \
    assert_equals_data, CITIES_INDEX_AND_COLUMNS, df_to_list


def check_set_const(constant, expected_series):
    bt = get_bt_with_test_data()
    bt['new_column'] = constant
    check_expected_db_type(bt, expected_series)
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding',  # original columns
            'new_column'  # new
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, constant],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, constant],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, constant]
        ]
    )
    assert bt.new_column == bt['new_column']


def test_set_const_int():
    check_set_const(np.int64(4), BuhTuhSeriesInt64)
    check_set_const(5, BuhTuhSeriesInt64)

def test_set_const_float():
    check_set_const(5.1, BuhTuhSeriesFloat64)

def test_set_const_bool():
    check_set_const(True, BuhTuhSeriesBoolean)

def test_set_const_str():
    check_set_const('keatsen', BuhTuhSeriesString)

def test_set_const_date():
    check_set_const(datetime.date(2019,1,5), BuhTuhSeriesDate)

def test_set_const_datetime():
    check_set_const(datetime.datetime.now(), BuhTuhSeriesTimestamp)

def test_set_const_time():
    check_set_const(datetime.time.fromisoformat('00:05:23.283'), BuhTuhSeriesTime)

def test_set_const_timedelta():
        check_set_const(np.datetime64('2005-02-25T03:30') - np.datetime64('2005-01-25T03:30'), BuhTuhSeriesTimedelta)
        check_set_const(datetime.datetime.now() - datetime.datetime(2015,4,6), BuhTuhSeriesTimedelta)


def test_set_const_int_from_series():
    bt = get_bt_with_test_data()[['founding']]
    max = bt.groupby()['founding'].sum()
    max_series = max['founding_sum']
    max_value = max_series[1]
    bt['max_founding'] = max_value
    check_expected_db_type(bt, BuhTuhSeriesInt64, 'max_founding')

    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'founding',  # original columns
            'max_founding'  # new
        ],
        expected_data=[
            [1, 1285, 4009], [2, 1456, 4009], [3, 1268, 4009]
        ]
    )
    assert bt.max_founding == bt['max_founding']


def test_set_series_column():
    bt = get_bt_with_test_data()
    bt['duplicated_column'] = bt['founding']
    check_expected_db_type(bt, BuhTuhSeriesInt64, 'duplicated_column')
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268],
        ]
    )
    assert bt.duplicated_column == bt['duplicated_column']

    bt['spaces in column'] = bt['founding']
    assert_equals_data(
        bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 1456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 1268],
        ]
    )

    filtered_bt = bt[bt['city'] == 'Ljouwert']
    filtered_bt['town'] = filtered_bt['city']
    assert_equals_data(
        filtered_bt,
        expected_columns=[
            '_index_skating_order',  # index
            'skating_order', 'city', 'municipality', 'inhabitants', 'founding', 'duplicated_column', 'spaces in column', 'town'
        ],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 1285, 'Ljouwert']
        ]
    )
    assert filtered_bt.town == filtered_bt['town']


def test_set_multiple():
    bt = get_bt_with_test_data()
    bt['duplicated_column'] = bt['founding']
    bt['alternative_sport'] = 'keatsen'
    bt['leet'] = 1337
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['duplicated_column', 'alternative_sport', 'leet'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 1285, 'keatsen', 1337],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 1456, 'keatsen', 1337],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 1268, 'keatsen', 1337]
        ]
    )
    assert bt.duplicated_column == bt['duplicated_column']
    assert bt.alternative_sport == bt['alternative_sport']
    assert bt.leet == bt['leet']


def test_set_existing():
    bt = get_bt_with_test_data()
    bt['city'] = bt['founding']
    check_expected_db_type(bt, BuhTuhSeriesInt64, 'city')
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 1285, 'Leeuwarden', 93485, 1285],
            [2, 2, 1456, 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 1268, 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.city == bt['city']


def test_set_existing_referencing_other_column_experience():
    bt = get_bt_with_test_data()
    bt['city'] = bt['city'] + ' test'
    check_expected_db_type(bt, BuhTuhSeriesString, 'city')
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 1, 'Ljouwert test', 'Leeuwarden', 93485, 1285],
            [2, 2, 'Snits test', 'Súdwest-Fryslân', 33520, 1456],
            [3, 3, 'Drylts test', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.city == bt['city']

    bt = get_bt_with_test_data()
    a = bt['city'] + ' test1'
    b = bt['city'] + ' test2'
    c = bt['skating_order'] + bt['skating_order']
    bt['skating_order'] = 0
    bt['city'] = ''
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 0, '', 'Leeuwarden', 93485, 1285],
            [2, 0, '', 'Súdwest-Fryslân', 33520, 1456],
            [3, 0, '', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    bt['skating_order'] = c
    bt['city'] = a + ' - ' + b
    check_expected_db_type(bt, BuhTuhSeriesInt64, 'skating_order')
    check_expected_db_type(bt, BuhTuhSeriesString, 'city')
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS,
        expected_data=[
            [1, 2, 'Ljouwert test1 - Ljouwert test2', 'Leeuwarden', 93485, 1285],
            [2, 4, 'Snits test1 - Snits test2', 'Súdwest-Fryslân', 33520, 1456],
            [3, 6, 'Drylts test1 - Drylts test2', 'Súdwest-Fryslân', 3055, 1268]
        ]
    )
    assert bt.skating_order == bt['skating_order']
    assert bt.city == bt['city']


def test_set_series_expression():
    bt = get_bt_with_test_data()
    bt['time_travel'] = bt['founding'] + 1000
    check_expected_db_type(bt, BuhTuhSeriesInt64, 'time_travel')
    assert_equals_data(
        bt,
        expected_columns=CITIES_INDEX_AND_COLUMNS + ['time_travel'],
        expected_data=[
            [1, 1, 'Ljouwert', 'Leeuwarden', 93485, 1285, 2285],
            [2, 2, 'Snits', 'Súdwest-Fryslân', 33520, 1456, 2456],
            [3, 3, 'Drylts', 'Súdwest-Fryslân', 3055, 1268, 2268]
        ]
    )
    assert bt.time_travel == bt['time_travel']
