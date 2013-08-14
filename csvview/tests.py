# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse

from csvview.views import CsvView, encode_header

from testproject.testproject.models import Car, Manufacturer


class AttrGetterTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='Jeep',
        )
        self.car = self.manufacturer.car_set.create(
            name='Grand Cherokee',
        )

    def test_lambda(self):
        class View(CsvView):
            model = Car
            headers = [('Name', lambda x: x.name)]

        self.assertEqual(View().get_row(self.car), ['Grand Cherokee'])

    def test_simple_attr(self):
        class View(CsvView):
            model = Car
            headers = [('Name', 'name')]

        self.assertEqual(View().get_row(self.car), ['Grand Cherokee'])

    def test_dotted_path(self):
        class View(CsvView):
            model = Car
            headers = [('Name', 'manufacturer.name')]

        self.assertEqual(View().get_row(self.car), ['Jeep'])

    def test_callable(self):
        class View(CsvView):
            model = Car
            headers = [('Name', 'get_display_name')]

        self.assertEqual(View().get_row(self.car), ['GRAND CHEROKEE'])


class CsvViewTest(TestCase):
    def setUp(self):
        self.manufacturer = Manufacturer.objects.create(
            name='你好凯兰',
        )

    def test_unicode_csv_output(self):
        # In Python 2, the built-in csv library doesn't handle unicode.
        response = self.client.get(reverse('manufacturers'))
        expected = "Name,Number of models\r\n你好凯兰,0\r\n".encode('utf8')
        self.assertEqual(response.content, expected)

    def test_content_type(self):
        response = self.client.get(reverse('manufacturers'))
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_filename_autogenerated(self):
        response = self.client.get(reverse('manufacturers'))
        expected = 'attachment; filename="manufacturer_list.csv"'
        self.assertEqual(response['Content-Disposition'], expected)

    def test_unicode_filename(self):
        response = self.client.get(reverse('unicode_filename'))
        # It is kinda weird to have Unicode in the headers.  Copied the encoder
        # from Django.
        expected = encode_header('attachment; filename="áèïôų.csv"')
        self.assertEqual(response['Content-Disposition'], expected)
