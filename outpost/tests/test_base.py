from django.test import TestCase
from django.db import models
from outpost.models import SyncableModel


class TestModel(SyncableModel):
    data = models.CharField(max_length=5)


class SyncModelTestCase(TestCase):
    def setUp(self):
        TestModel.objects.create(data="Foo!!")
        TestModel.objects.create(data="Bar!!")

    def test_save_works_basic(self):
        d = TestModel.objects.get(data="Foo!!")
        self.assertEqual("Foo!!", d.data)
