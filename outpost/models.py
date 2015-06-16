from django.db import models


class Outpost(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
