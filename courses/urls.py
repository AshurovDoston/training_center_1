from django.urls import path
from .views import course_list, course_detail, lesson_detail

urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>/", course_detail, name="course_detail"),
    path(
        "<slug:course_slug>/lessons/<int:lesson_id>/",
        lesson_detail,
        name="lesson_detail",
    ),
]
