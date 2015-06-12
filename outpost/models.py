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
        return {field.name: field.value_to_string(self)
                for field in self._meta.local_fields}

    @classmethod
    def hydrate(cls, data):
        instance = cls()
        fields = {field.name: field for field in cls._meta.local_fields}
        for k, v in data.items():
            sdata, field = (data[k], fields[k])
            setattr(instance, k, field.to_python(sdata))
        return instance

    @classmethod
    def get_queue(cls):
        if SyncableModel._sync_queue is None:
            SyncableModel._sync_queue = queue.Queue(maxsize=0)
        return SyncableModel._sync_queue

    @classmethod
    def get_models(cls):
        return SyncableModel.__subclasses__()

    @classmethod
    def _catchup(cls, when):
        q = cls.get_queue()
        for obj in cls.objects.filter(when__gte=when).distinct():
            q.put(obj)

    @classmethod
    def _stawp(cls):
        SyncableModel._sync_queue = None

    def save(self, *args, **kwargs):
        if SyncableModel._sync_queue is not None:
            SyncableModel._sync_queue.put(self)

        return super(SyncableModel, self).save(*args, **kwargs)
