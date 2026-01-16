from django.db import models
from core.models import SoftDeleteModel


class Student(SoftDeleteModel):
    user = models.OneToOneField("accounts.CustomUser", on_delete=models.CASCADE, related_name="student_profile")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return f"Student: {self.user.username}"
        # return f"Student: {self.user.get_username()}"


class Instructor(SoftDeleteModel):
    user = models.OneToOneField("accounts.CustomUser", on_delete=models.CASCADE, related_name="instructor_profile")
    bio = models.TextField(blank=True, help_text="Instructor's biography or introduction")

    class Meta:
        verbose_name = "Instructor"
        verbose_name_plural = "Instructors"

    def __str__(self):
        return f"Instructor: {self.user.username}"
