import pandas as pd
import numpy as np
import json

from django.test import TestCase

from treenipaivakirja.utils import duration_to_string, duration_to_decimal, speed_min_per_km, dataframe_to_dict, coalesce


class DurationToStringTest(TestCase):
    def test_none(self):
        h = None
        mins = None
        self.assertEqual(duration_to_string(h,mins),None)

    def test_nan(self):
        h = np.nan
        mins = np.nan
        self.assertEqual(duration_to_string(h,mins),None)

    def test_h_only(self):
        h = 15
        mins = None
        self.assertEqual(duration_to_string(h,mins),'15:00')

    def test_min_only(self):
        h = None
        mins = 25
        self.assertEqual(duration_to_string(h,mins),'00:25')

    def test_small_integers(self):
        h = 1
        mins = 1
        self.assertEqual(duration_to_string(h,mins),'01:01')

    def test_decimals(self):
        h = 1.5
        mins = 1.2
        self.assertEqual(duration_to_string(h,mins),'01:01')

    def test_min_greater_than_60(self):
        h = 1
        mins = 100
        self.assertEqual(duration_to_string(h,mins),'02:40')

    def test_min_only_and_greater_than_60(self):
        h = None
        mins = 75
        self.assertEqual(duration_to_string(h,mins),'01:15')


class DurationToDecimalTest(TestCase):
    def test_none(self):
        h = None
        mins = None
        self.assertEqual(duration_to_decimal(h,mins),0)

    def test_nan(self):
        h = np.nan
        mins = np.nan
        self.assertEqual(duration_to_decimal(h,mins),0)

    def test_h_only(self):
        h = 2
        mins = None
        self.assertEqual(duration_to_decimal(h,mins),2)

    def test_min_only(self):
        h = None
        mins = 15
        self.assertEqual(duration_to_decimal(h,mins),0.25)

    def test_min_greater_than_60(self):
        h = 1
        mins = 90
        self.assertEqual(duration_to_decimal(h,mins),2.5)


class SpeedMinPerKmTest(TestCase):
    def test_none(self):
        m = None
        s = None
        self.assertEqual(speed_min_per_km(m,s),None)
    
    def test_h_only(self):
        m = 5
        s = None
        self.assertEqual(speed_min_per_km(m,s),5)
    
    def test_min_only(self):
        m = None
        s = 30
        self.assertEqual(speed_min_per_km(m,s),0.5)

    def test_integers(self):
        m = 3
        s = 15
        self.assertEqual(speed_min_per_km(m,s),3.25)

    def test_s_greater_than_60(self):
        m = 10
        s = 72
        self.assertEqual(speed_min_per_km(m,s),11.2)


class DataFrameToDictTest(TestCase):
    def test_empty_df(self):
        df = pd.DataFrame()
        self.assertEqual(dataframe_to_dict(df),[])

    def test_df_with_no_rows(self):
        df = pd.DataFrame(columns=['A','B','C'])
        self.assertEqual(dataframe_to_dict(df),[])

    def test_df_with_rows(self):
        categories = ['A','B']
        data = {'col1': [1, 2], 'col2': [3, 4]}
        df = pd.DataFrame(data, index=categories)
        result = [{"category": "A", "series": {"col1": 1, "col2": 3}}, {"category": "B", "series": {"col1": 2, "col2": 4}}]
        self.assertEqual(dataframe_to_dict(df),result)


class CoalesceTest(TestCase):
    def test_none(self):
        x = None
        val = 'kissa'
        self.assertEqual(coalesce(x,val),'kissa')

    def test_nan(self):
        x = np.nan
        val = 'kissa'
        self.assertEqual(coalesce(x,val),'kissa')

    def test_not_none(self):
        x = 'koira'
        val = 'kissa'
        self.assertEqual(coalesce(x,val),'koira')