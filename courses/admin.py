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
    list_display = ("title", "modules_count", "instructor", "slug", "created_at")
    search_fields = ("title", "description", "instructor__user__username", "instructor__user__email")
    list_filter = ("is_deleted", "created_at", "updated_at")
    # prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("slug",)
    ordering = ("-created_at",)
    list_select_related = ("instructor", "instructor__user",)
    inlines = [ModuleInline]

    def modules_count(self, obj):
        return obj.modules.count()
    
    modules_count.short_description = "Modules"

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title", "order", "is_deleted")
    ordering = ("order",)
    show_change_link = True

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "course", "created_at")
    search_fields = ("title", "course__title", "course__instructor__user__username")
    list_filter = ("is_deleted", "created_at", "updated_at")
    ordering = ("order",)
    list_select_related = ("course", "course__instructor", "course__instructor__user",)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order", "created_at")
    search_fields = ("title", "module__title", "module__course__title")
    list_filter = ("is_deleted", "created_at", "updated_at")
    ordering = ("module", "order")
    list_select_related = ("module", "module__course",)