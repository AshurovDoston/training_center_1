from django.db import models
from django.utils import timezone

from core.managers import AllObjectsManager, SoftDeleteManager


class TimestampedModel(models.Model):
    """
    Abstract base model that provides automatic timestamp tracking.

    All models inheriting from this will automatically have:
    - created_at: Set once when the record is first created
    - updated_at: Updated every time the record is saved
    """

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimestampedModel):
    """
    Abstract base model that provides soft delete functionality.

    Instead of permanently deleting records, this model marks them as deleted
    by setting is_deleted=True and recording the deletion timestamp.

    Inherits from TimestampedModel:
    - created_at: Set once when the record is first created
    - updated_at: Updated every time the record is saved

    Adds soft delete fields:
    - is_deleted: Boolean flag indicating if record is "deleted"
    - deleted_at: Timestamp of when the record was soft deleted

    Managers:
    - objects: Default manager that excludes deleted records
    - all_objects: Manager that includes all records (deleted and non-deleted)
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Override Django's delete() to perform a soft delete instead.

        Sets is_deleted=True and records the deletion timestamp.
        The record remains in the database but is marked as deleted.
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database.

        This method has an explicit name to prevent accidental data loss.
        Use with caution - this action cannot be undone.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        Restore a soft-deleted record.

        Clears the is_deleted flag and deleted_at timestamp,
        making the record active again.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
