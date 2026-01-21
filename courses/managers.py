from django.db.models import Count

from core.managers import SoftDeleteQuerySet, SoftDeleteManager, AllObjectsManager


class CourseQuerySet(SoftDeleteQuerySet):
    """
    Custom QuerySet for Course model with pre-built count annotations.
    """

    def with_full_counts(self):
        """
        Annotate courses with modules, lessons, and enrollments counts.

        Usage:
            Course.objects.with_full_counts()
            # Each course has: modules_count, lessons_count, enrollments_count
        """
        return self.annotate(
            modules_count=Count("modules", distinct=True),
            lessons_count=Count("modules__lessons", distinct=True),
            enrollments_count=Count("enrollments", distinct=True),
        )


class CourseManager(SoftDeleteManager):
    """
    Default manager for Course that excludes soft-deleted records.
    """

    def get_queryset(self):
        return CourseQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        return CourseQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return CourseQuerySet(self.model, using=self._db).filter(is_deleted=True)

    def with_full_counts(self):
        return self.get_queryset().with_full_counts()

    def with_counts(self, *relations):
        return self.get_queryset().with_counts(*relations)


class CourseAllObjectsManager(AllObjectsManager):
    """
    Manager for Course that includes all records (deleted and non-deleted).
    """

    def get_queryset(self):
        return CourseQuerySet(self.model, using=self._db)

    def with_full_counts(self):
        return self.get_queryset().with_full_counts()

    def with_counts(self, *relations):
        return self.get_queryset().with_counts(*relations)


class ModuleQuerySet(SoftDeleteQuerySet):
    """
    Custom QuerySet for Module model with pre-built count annotations.
    """

    def with_lessons_count(self):
        """
        Annotate modules with lessons count.

        Usage:
            Module.objects.with_lessons_count()
            # Each module has: lessons_count
        """
        return self.annotate(lessons_count=Count("lessons", distinct=True))


class ModuleManager(SoftDeleteManager):
    """
    Default manager for Module that excludes soft-deleted records.
    """

    def get_queryset(self):
        return ModuleQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        return ModuleQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return ModuleQuerySet(self.model, using=self._db).filter(is_deleted=True)

    def with_lessons_count(self):
        return self.get_queryset().with_lessons_count()

    def with_counts(self, *relations):
        return self.get_queryset().with_counts(*relations)


class ModuleAllObjectsManager(AllObjectsManager):
    """
    Manager for Module that includes all records (deleted and non-deleted).
    """

    def get_queryset(self):
        return ModuleQuerySet(self.model, using=self._db)

    def with_lessons_count(self):
        return self.get_queryset().with_lessons_count()

    def with_counts(self, *relations):
        return self.get_queryset().with_counts(*relations)
