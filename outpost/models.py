from django.db import models


class Outpost(models.Model):
    class Meta:
        app_label = "outpost"

    id = models.CharField(max_length=16, primary_key=True)
