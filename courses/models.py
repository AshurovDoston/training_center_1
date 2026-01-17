from django.db import models
from core.models import SoftDeleteModel
from core.mixins import SlugMixin
from profiles.models import Instructor, Student


class Course(SlugMixin, SoftDeleteModel):
    """
    A complete learning product created by an instructor.

    Course is the top level of the content hierarchy:
    Course → Module → Lesson

    Inherits from:
        - SlugMixin: Provides auto-generated slug from title for SEO-friendly URLs
        - SoftDeleteModel: Provides timestamps and soft delete functionality

    Inherited fields:
        From SlugMixin:
            - slug: Auto-generated from title, unique, used in URLs
        From SoftDeleteModel:
            - created_at, updated_at, is_deleted, deleted_at

    Managers:
        - objects: Returns only active (non-deleted) courses
        - all_objects: Returns all courses including soft-deleted
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name="courses")

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Module(SoftDeleteModel):
    """
    A logical grouping of lessons within a course.

    Modules organize lessons into chapters/sections. A course contains
    multiple modules, and each module contains multiple lessons.

    Inherits from SoftDeleteModel:
        - created_at, updated_at, is_deleted, deleted_at

    No SlugMixin because:
        - Modules are accessed through their parent course
        - URL pattern: /courses/<course-slug>/modules/<module-id>/
        - No SEO benefit for nested content
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="modules")
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ["order"]

    ### If you want to enforce unique ordering of modules within a course, uncomment below:
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["course", "order"], name="unique_module_order_per_course"),
        ]


    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(SoftDeleteModel):
    """
    A single unit of learning content within a module.

    Lessons are the atomic unit of content that students consume.
    Each lesson belongs to exactly one module.

    Inherits from SoftDeleteModel:
        - created_at, updated_at, is_deleted, deleted_at

    No SlugMixin because:
        - Lessons are accessed through their parent module and course
        - URL pattern: /courses/<course-slug>/modules/<id>/lessons/<id>/
        - No SEO benefit for deeply nested content
    """

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ["order"]

    ### If you want to enforce unique ordering of lessons within a module, uncomment below:
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["module", "order"], name="unique_lesson_order_per_module"),
        ]


    def __str__(self):
        return f"{self.module.title} - {self.title}"
