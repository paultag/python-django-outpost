from django.test import TestCase
from .models import TestModel
from outpost.sync import sync
import queue


class SyncBackend:
    def __init__(self, host, auth):
        self.out = queue.Queue(maxsize=1)

    def sync(self, obj):
        self.out.put(obj)



class SyncBackendTestCase(TestCase):
    def setUp(self):
        self.sync = sync(host=None, auth=None, backend=SyncBackend)

    def tearDown(self):
        self.sync.stop()

    def test_save_works_sync(self):
        TestModel.objects.create(data="Foo!!")
        el = self.sync.backend.out.get()
        self.assertEqual(el.data, "Foo!!")
