from django.db import models
from core.models import SoftDeleteModel
from accounts.models import CustomUser


class Student(SoftDeleteModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="student_profile"
    )

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.user.get_username()


class Instructor(SoftDeleteModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="instructor_profile"
    )
    bio = models.TextField(
        blank=True, help_text="Instructor's biography or introduction"
    )

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"

    def __str__(self):
        return self.user.get_username()
