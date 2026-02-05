from django.shortcuts import render
from django.views.generic import DetailView
from .models import Course, Lesson


def course_list(request):
    courses = Course.objects.with_full_counts().select_related("instructor__user")
    context = {
        "courses": courses,
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, slug):
    course = (
        Course.objects.select_related("instructor__user")
        .prefetch_related("modules__lessons")
        .get(slug=slug)
    )
    context = {
        "course": course,
    }
    return render(request, "courses/course_detail.html", context)


class LessonDetailView(DetailView):
    """
    Display a single lesson with navigation to previous/next lessons.

    URL: /courses/<course_slug>/lessons/<lesson_id>/
    """

    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"
    pk_url_kwarg = "lesson_id"

    def get_queryset(self):
        """Filter lessons to only those belonging to the specified course."""
        return Lesson.objects.select_related("module__course__instructor__user").filter(
            module__course__slug=self.kwargs["course_slug"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        course = lesson.module.course

        # Re-fetch course with prefetch_related so the sidebar template can
        # iterate course.modules.all → module.lessons.all without N+1 queries.
        course = (
            Course.objects.prefetch_related("modules__lessons")
            .select_related("instructor__user")
            .get(pk=course.pk)
        )

        # Get all lessons in this course, ordered by module order then lesson order
        all_lessons = list(
            Lesson.objects.filter(module__course=course)
            .select_related("module")
            .order_by("module__order", "order")
        )

        # Find current lesson's position and get prev/next
        current_index = next(
            (i for i, l in enumerate(all_lessons) if l.pk == lesson.pk), None
        )

        context["course"] = course
        context["previous_lesson"] = (
            all_lessons[current_index - 1]
            if current_index and current_index > 0
            else None
        )
        context["next_lesson"] = (
            all_lessons[current_index + 1]
            if current_index is not None and current_index < len(all_lessons) - 1
            else None
        )

        return context


lesson_detail = LessonDetailView.as_view()
