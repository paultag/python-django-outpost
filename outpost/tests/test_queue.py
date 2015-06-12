from django.test import TestCase
from .models import TestModel



class SyncModelQueueTestCase(TestCase):
    def test_save_works_queue(self):
        TestModel.objects.create(data="Foo!!")
        d = TestModel.objects.get(data="Foo!!")
        self.assertEqual("Foo!!", d.data)

        queue = TestModel.get_queue()
        self.assertTrue(queue.empty())

        TestModel.objects.create(data="Bar!!")

        queue = TestModel.get_queue()
        self.assertFalse(queue.empty())
        el = queue.get()

        self.assertEqual("Bar!!", el.data)
