from django.test import TestCase
from .models import TestModel
from outpost.models import SyncableModel



class SyncModelTestCase(TestCase):
    def setUp(self):
        TestModel.objects.create(data="Foo!!")
        TestModel.objects.create(data="Bar!!")

    def test_save_works_basic(self):
        d = TestModel.objects.get(data="Foo!!")
        self.assertEqual("Foo!!", d.data)

    def test_search_works(self):
        tm, = SyncableModel.get_models()
        self.assertEqual(tm, TestModel)

    def test_serialize_works_basic(self):
        d = TestModel.objects.get(data="Foo!!")
        s = d.serialize()
        self.assertEqual(s['id'], str(d.id))

    def test_hydrate_works_basic(self):
        d = TestModel.objects.get(data="Foo!!")
        count = TestModel.objects.count()

        s = d.serialize()
        data = TestModel.hydrate(s)
        data.save()
        self.assertEqual(data.id, d.id)

        self.assertEqual(TestModel.objects.count(), count)
