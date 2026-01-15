from django.db import models
from core.mixins import SlugMixin
from core.models import SoftDeleteModel

# Create your models here.
class SlugTestModel(SlugMixin, SoftDeleteModel):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Slug Test Model"
        verbose_name_plural = "Slug Test Models"

    def __str__(self):
        return f"{self.title} - ({self.slug})"