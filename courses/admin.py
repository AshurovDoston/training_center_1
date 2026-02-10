from django.contrib import admin
from .models import Course, Module, Lesson


# Register your models here.
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title", "order", "is_deleted")
    ordering = ("order",)
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "instructor",
        "modules_count",
        "lessons_count",
        "enrollments_count",
        "updated_at",
    )
    search_fields = (
        "title",
        "description",
        "instructor__user__username",
        "instructor__user__email",
    )
    list_filter = ("instructor", "is_deleted", "updated_at")
    readonly_fields = ("slug",)
    ordering = ("-updated_at",)
    list_select_related = (
        "instructor",
        "instructor__user",
    )
    inlines = [ModuleInline]

    def get_queryset(self, request):
        return super().get_queryset(request).with_full_counts()

    @admin.display(description="Modules")
    def modules_count(self, obj):
        return obj.modules_count

    @admin.display(description="Lessons")
    def lessons_count(self, obj):
        return obj.lessons_count

    @admin.display(description="Enrollments")
    def enrollments_count(self, obj):
        return obj.enrollments_count


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "order", "video", "is_deleted")
    ordering = ("order",)
    show_change_link = True


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "lessons_count", "order", "updated_at")
    search_fields = ("title", "course__title", "course__instructor__user__username")
    list_filter = ("course", "is_deleted", "updated_at")
    ordering = ("course", "order")
    list_select_related = (
        "course",
        "course__instructor",
        "course__instructor__user",
    )
    inlines = [LessonInline]

    def get_queryset(self, request):
        return super().get_queryset(request).with_lessons_count()

    @admin.display(description="Lessons")
    def lessons_count(self, obj):
        return obj.lessons_count


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "module",
        "get_course",
        "order",
        "has_content",
        "has_video",
        "updated_at",
    )
    search_fields = ("title", "module__title", "module__course__title")
    list_filter = ("module__course", "module", "is_deleted", "updated_at")
    ordering = ("module", "order")
    list_select_related = (
        "module",
        "module__course",
    )

    @admin.display(description="Course")
    def get_course(self, obj):
        return obj.module.course

    @admin.display(description="Content?", boolean=True)
    def has_content(self, obj):
        return bool(obj.content)

    @admin.display(description="Video?", boolean=True)
    def has_video(self, obj):
        return bool(obj.video)