from django.db import models
from django.utils import timezone
from core.models import SoftDeleteModel
from courses.models import Course, Lesson
from profiles.models import Student


# Create your models here.
class Enrollment(SoftDeleteModel):
    """
    Trsacks a student's enrollment and progress in a course.

    Uses PROTECT on delete to prevent accidental data loss.
    Admin must soft-delete enrollments before deleting Student/Course.
    """

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class LessonProgress(SoftDeleteModel):
    """
    Tracks a student's progress on individual lessons.

    CASCADE from Enrollment: if enrollment deleted, progress goes too.
    PROTECT from Lesson: can't delete lesson if students have progress.
    """

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.PROTECT, related_name="lesson_progress"
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progress"
        unique_together = ("enrollment", "lesson")
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.enrollment.student} on {self.lesson}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.is_completed:
            self.completed_at = None
        super().save(*args, **kwargs)
