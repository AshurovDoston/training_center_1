from django.contrib import admin
from .models import Enrollment, LessonProgress

# Register your models here.


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 1
    fields = ("lesson", "is_completed", "completed_at", "is_deleted")
    readonly_fields = ("completed_at",)
    ordering = ("lesson__module__order", "lesson__order")
    show_change_link = True


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "progress_display", "enrolled_at")
    search_fields = ("student__user__username", "student__user__email", "course__title")
    list_filter = ("course", "student", "is_deleted", "enrolled_at")
    ordering = ("course",)
    list_select_related = (
        "student",
        "student__user",
        "course",
    )
    readonly_fields = ("enrolled_at",)
    inlines = [LessonProgressInline]

    @admin.display(description="Progress")
    def progress_display(self, obj):
        from courses.models import Lesson

        total_lessons = Lesson.objects.filter(module__course=obj.course).count()
        if total_lessons == 0:
            return "0/0 (0%)"
        completed_lessons = obj.lesson_progress.filter(is_completed=True).count()
        percentage = int((completed_lessons / total_lessons) * 100)
        return f"{completed_lessons}/{total_lessons} ({percentage}%)"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "lesson",
        "is_completed",
        "completed_at",
        "created_at",
    )
    search_fields = (
        "enrollment__student__user__username",
        "enrollment__course__title",
        "lesson__title",
    )
    list_filter = ("is_deleted", "is_completed", "created_at", "updated_at")
    ordering = ("-completed_at",)
    list_select_related = (
        "enrollment",
        "enrollment__student",
        "enrollment__student__user",
        "enrollment__course",
        "lesson",
    )
    readonly_fields = ("completed_at",)
