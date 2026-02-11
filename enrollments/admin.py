from django.contrib import admin
from django.db.models import Count, Q, Subquery, OuterRef

from .models import Enrollment, LessonProgress


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
    search_fields = (
        "student__user__username",
        "student__user__email",
        "course__title",
    )
    list_filter = ("course", "student", "is_deleted", "enrolled_at")
    ordering = ("course",)
    list_select_related = (
        "student",
        "student__user",
        "course",
    )
    readonly_fields = ("enrolled_at",)
    inlines = [LessonProgressInline]

    def get_queryset(self, request):
        from courses.models import Lesson

        qs = super().get_queryset(request)
        # Annotate total lessons per course and completed lessons per enrollment
        total_subquery = (
            Lesson.objects.filter(module__course=OuterRef("course"), is_deleted=False)
            .values("module__course")
            .annotate(cnt=Count("id"))
            .values("cnt")
        )
        return qs.annotate(
            _total_lessons=Subquery(total_subquery),
            _completed_lessons=Count(
                "lesson_progress",
                filter=Q(
                    lesson_progress__is_completed=True,
                    lesson_progress__is_deleted=False,
                ),
            ),
        )

    @admin.display(description="Progress")
    def progress_display(self, obj):
        total = obj._total_lessons or 0
        completed = obj._completed_lessons or 0
        if total == 0:
            return "0/0 (0%)"
        percentage = int((completed / total) * 100)
        return f"{completed}/{total} ({percentage}%)"


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
