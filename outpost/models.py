from django.db import models
import queue
import uuid


class SyncableModel(models.Model):
    _sync_queue = None

    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    when = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        pass

    @classmethod
    def get_queue(cls):
        if SyncableModel._sync_queue is None:
            SyncableModel._sync_queue = queue.Queue(maxsize=0)
        return SyncableModel._sync_queue


    def save(self, *args, **kwargs):
        if SyncableModel._sync_queue is not None:
            SyncableModel._sync_queue.put(self)

        return super(SyncableModel, self).save(*args, **kwargs)
