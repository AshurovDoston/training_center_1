from django.db import models
from django.db.models import Count
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that provides soft delete operations.

    All methods return QuerySet instances, enabling method chaining:
    Course.objects.filter(status="draft").active().order_by("-created_at")
    """

    def active(self):
        """
        Filter to non-deleted records only.

        Useful when you have a QuerySet that might include deleted records
        (e.g., from all_objects) and want to filter them out.
        """
        return self.filter(is_deleted=False)

    def deleted(self):
        """
        Filter to deleted records only.

        Useful for admin interfaces showing "trash" or for cleanup tasks.
        """
        return self.filter(is_deleted=True)

    def soft_delete(self):
        """
        Bulk soft delete all records in the QuerySet.

        Returns the number of records updated.
        This is what gets called when you do QuerySet.delete().
        """
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """
        Permanently delete all records in the QuerySet.

        Explicitly named to prevent accidents. Calls Django's original delete().
        Returns tuple: (total_deleted, {model_label: count})
        """
        return super().delete()

    def restore(self):
        """
        Bulk restore all soft-deleted records in the QuerySet.

        Returns the number of records updated.
        """
        return self.update(is_deleted=False, deleted_at=None)

    def delete(self):
        """
        Override delete() to perform soft delete instead.

        This ensures bulk operations like:
            Course.objects.filter(status="draft").delete()
        perform soft delete, not hard delete.
        """
        return self.soft_delete()

    def with_counts(self, *relations):
        """
        Annotate queryset with counts for specified relations.

        Handles nested relations by replacing '__' with '_' in the field name.

        Usage:
            Course.objects.with_counts('modules', 'enrollments')
            # Adds: modules_count, enrollments_count

            Course.objects.with_counts('modules__lessons')
            # Adds: modules_lessons_count
        """
        annotations = {}
        for relation in relations:
            field_name = f"{relation.replace('__', '_')}_count"
            annotations[field_name] = Count(relation, distinct=True)
        return self.annotate(**annotations)


class SoftDeleteManager(models.Manager):
    """
    Default manager that excludes soft-deleted records.

    This manager is assigned to `objects`, making soft delete transparent:
    Course.objects.all() returns only non-deleted courses.
    """

    def get_queryset(self):
        """
        Return a QuerySet that excludes deleted records.

        This is the "factory method" called every time you access
        Course.objects. By filtering here, all subsequent operations
        automatically exclude deleted records.
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        """
        Return a QuerySet including deleted records.

        Useful when you need to access everything:
        Course.objects.with_deleted().filter(created_at__year=2024)
        """
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """
        Return a QuerySet with only deleted records.

        Useful for admin "trash" views:
        Course.objects.deleted_only()
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)


class AllObjectsManager(models.Manager):
    """
    Manager that includes all records (deleted and non-deleted).

    Assigned to `all_objects` for explicit access to everything.
    """

    def get_queryset(self):
        """
        Return an unfiltered QuerySet.

        No is_deleted filter applied - returns everything.
        """
        return SoftDeleteQuerySet(self.model, using=self._db)
