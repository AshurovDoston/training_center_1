from django.urls import path

from enrollments.views import enroll_in_course

from .views import course_list, course_detail, lesson_detail

urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>/", course_detail, name="course_detail"),
    path("<slug:slug>/enroll/", enroll_in_course, name="enroll_in_course"),
    path(
        "<slug:course_slug>/lessons/<int:lesson_id>/",
        lesson_detail,
        name="lesson_detail",
    ),
]
