from django.test import TestCase
from .models import TestModel



class SyncModelTestCase(TestCase):
    def setUp(self):
        TestModel.objects.create(data="Foo!!")
        TestModel.objects.create(data="Bar!!")

    def test_save_works_basic(self):
        d = TestModel.objects.get(data="Foo!!")
        self.assertEqual("Foo!!", d.data)
