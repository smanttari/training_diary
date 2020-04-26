from datetime import date

from django.test import TestCase

from treenipaivakirja.forms import KausiForm


class KausiFormTest(TestCase):
    def test_alkupvm_smaller_than_loppupvm(self):
        alkupvm = date(2020,1,1)
        loppupvm = date(2020,1,2)
        form = KausiForm(data={
            'kausi': 'Season1', 
            'alkupvm': alkupvm, 
            'loppupvm': loppupvm, 
            'user': 1
            })
        self.assertTrue(form.is_valid())

    def test_alkupvm_greater_than_loppupvm(self):
        alkupvm = date(2020,1,1)
        loppupvm = date(2019,12,31)
        form = KausiForm(data={
            'kausi': 'Season1', 
            'alkupvm': alkupvm, 
            'loppupvm': loppupvm, 
            'user': 1
            })
        self.assertFalse(form.is_valid())

    def test_alkupvm_equal_to_loppupvm(self):
        alkupvm = date(2020,1,1)
        loppupvm = alkupvm
        form = KausiForm(data={
            'kausi': 'Season1', 
            'alkupvm': alkupvm, 
            'loppupvm': loppupvm, 
            'user': 1
            })
        self.assertTrue(form.is_valid())
