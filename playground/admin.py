from django.contrib import admin
from .models import SlugTestModel


# Register your models here.
@admin.register(SlugTestModel)
class SlugTestModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "is_deleted",
        "deleted_at",
        "created_at",
        "updated_at",
    )
    search_fields = ("title", "slug")
    list_filter = ("is_deleted", "created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = ("slug", "created_at", "updated_at", "deleted_at")
