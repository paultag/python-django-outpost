from outpost.models import SyncableModel
from django.db import models


class TestModel(SyncableModel):
    data = models.CharField(max_length=5)
