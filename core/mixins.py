import uuid
from django.db import models
from django.utils.text import slugify


class UUIDMixin(models.Model):
    """
    Mixin that adds a UUID field for external-safe identification.

    Use this mixin when you need to expose record identifiers in URLs,
    APIs, or any external interface. The UUID prevents enumeration attacks
    and provides globally unique identifiers.

    Fields:
    - uuid: A unique, indexed UUID4 field for external identification

    Usage:
        class Course(UUIDMixin, SoftDeleteModel):
            title = models.CharField(max_length=200)

        # In URLs: /courses/550e8400-e29b-41d4-a716-446655440000/
        # Instead of: /courses/1/
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """
    Auto-generates a unique slug from `slug_source_field` (default: "title").

    Default behavior:
    - slug is generated only once (on first save)
    - slug remains stable even if title changes later
    """

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        editable=False,
    )

    slug_source_field = "title"

    class Meta:
        abstract = True

    def _get_slug_source_value(self) -> str:
        # returns the value of the field specified by slug_source_field
        value = getattr(self, self.slug_source_field, "") or ""
        return str(value).strip()

    def _generate_base_slug(self) -> str:
        base = slugify(self._get_slug_source_value())
        if not base:
            base = str(uuid.uuid4())[:8]  # fallback to random string if source is empty
        return base

    def _generate_unique_slug(self) -> str:
        base_slug = self._generate_base_slug()
        slug = base_slug
        ModelClass = self.__class__

        qs = (
            ModelClass.all_objects.all()
            if hasattr(ModelClass, "all_objects")
            else ModelClass.objects.all()
        )
        qs = qs.exclude(pk=self.pk)

        counter = 2
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        return super().save(*args, **kwargs)
