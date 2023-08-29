from django.db import models


class ModelInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
#TO DO deleted
    class Meta:
        abstract = True
        ordering = ("-updated_at", "-created_at")