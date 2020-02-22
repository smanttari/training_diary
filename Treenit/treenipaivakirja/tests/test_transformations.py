import pandas as pd
import numpy as np
import json

from django.test import TestCase

import treenipaivakirja.transformations as tr


class DurationToStringTest(TestCase):
    def test_none(self):
        h = None
        mins = None
        self.assertEqual(tr.duration_to_string(h,mins),'00:00')

    def test_nan(self):
        h = np.nan
        mins = np.nan
        self.assertEqual(tr.duration_to_string(h,mins),'00:00')

    def test_h_only(self):
        h = 15
        mins = None
        self.assertEqual(tr.duration_to_string(h,mins),'15:00')

    def test_min_only(self):
        h = None
        mins = 25
        self.assertEqual(tr.duration_to_string(h,mins),'00:25')

    def test_small_integers(self):
        h = 1
        mins = 1
        self.assertEqual(tr.duration_to_string(h,mins),'01:01')

    def test_decimals(self):
        h = 1.5
        mins = 1.2
        self.assertEqual(tr.duration_to_string(h,mins),'01:01')


class DurationToDecimalTest(TestCase):
    def test_none(self):
        h = None
        mins = None
        self.assertEqual(tr.duration_to_decimal(h,mins),0)

    def test_nan(self):
        h = np.nan
        mins = np.nan
        self.assertEqual(tr.duration_to_decimal(h,mins),0)

    def test_h_only(self):
        h = 2
        mins = None
        self.assertEqual(tr.duration_to_decimal(h,mins),2)

    def test_min_only(self):
        h = None
        mins = 15
        self.assertEqual(tr.duration_to_decimal(h,mins),0.25)

    def test_min_greater_than_60(self):
        h = 1
        mins = 90
        self.assertEqual(tr.duration_to_decimal(h,mins),2.5)


class VauhtiMinKmTest(TestCase):
    def test_none(self):
        m = None
        s = None
        self.assertEqual(tr.vauhti_min_km(m,s),None)
    
    def test_h_only(self):
        m = 5
        s = None
        self.assertEqual(tr.vauhti_min_km(m,s),5)
    
    def test_min_only(self):
        m = None
        s = 30
        self.assertEqual(tr.vauhti_min_km(m,s),0.5)

    def test_integers(self):
        m = 3
        s = 15
        self.assertEqual(tr.vauhti_min_km(m,s),3.25)

    def test_s_greater_than_60(self):
        m = 10
        s = 72
        self.assertEqual(tr.vauhti_min_km(m,s),11.2)


class DataFrameToJsonTest(TestCase):
    def test_empty_df(self):
        df = pd.DataFrame()
        self.assertEqual(tr.dataframe_to_json(df),json.dumps([]))

    def test_df_with_no_rows(self):
        df = pd.DataFrame(columns=['A','B','C'])
        self.assertEqual(tr.dataframe_to_json(df),json.dumps([]))

    def test_df_with_rows(self):
        categories = ['A','B']
        data = {'col1': [1, 2], 'col2': [3, 4]}
        df = pd.DataFrame(data, index=categories)
        result = [{"category": "A", "series": {"col1": 1, "col2": 3}}, {"category": "B", "series": {"col1": 2, "col2": 4}}]
        self.assertEqual(tr.dataframe_to_json(df),json.dumps(result))


class CoalesceTest(TestCase):
    def test_none(self):
        x = None
        val = 'kissa'
        self.assertEqual(tr.coalesce(x,val),'kissa')

    def test_nan(self):
        x = np.nan
        val = 'kissa'
        self.assertEqual(tr.coalesce(x,val),'kissa')

    def test_not_none(self):
        x = 'koira'
        val = 'kissa'
        self.assertEqual(tr.coalesce(x,val),'koira')