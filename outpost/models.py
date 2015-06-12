from django.db import models
import uuid


class SyncableModel(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    when = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        pass

    def save(self, *args, **kwargs):
        return super(SyncableModel, self).save(*args, **kwargs)
