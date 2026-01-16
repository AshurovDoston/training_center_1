from django.contrib import admin
from .models import Student, Instructor
# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_deleted", "deleted_at", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("is_deleted", "created_at", "updated_at")

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "is_deleted", "deleted_at", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "bio")
    list_filter = ("is_deleted", "created_at", "updated_at")