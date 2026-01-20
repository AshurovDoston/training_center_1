from django.contrib import admin
from django.db.models import Count
from .models import Enrollment, LessonProgress
# Register your models here.

class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 1
    fields = ("lesson", "is_completed", "completed_at", "is_deleted")
    readonly_fields = ("completed_at",)
    ordering = ("lesson",)
    show_change_link = True

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("course", "student_count", "student", "enrolled_at")
    search_fields = ("student__user__username", "student__user__email", "course__title")
    list_filter = ("is_deleted", "created_at", "updated_at")
    ordering = ("course",)
    list_select_related = ("student", "student__user", "course",)
    readonly_fields = ("enrolled_at",)
    inlines = [LessonProgressInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(student_count=Count("course__enrollments"))
        return queryset

    @admin.display(description="Enrolled")
    def student_count(self, obj):
        return obj.student_count



@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "is_completed", "completed_at", "created_at")
    search_fields = ("enrollment__student__user__username", "enrollment__course__title", "lesson__title")
    list_filter = ("is_deleted", "is_completed", "created_at", "updated_at")
    ordering = ("-completed_at",)
    list_select_related = ("enrollment", "enrollment__student", "enrollment__student__user", "enrollment__course", "lesson",)
    readonly_fields = ("completed_at",)