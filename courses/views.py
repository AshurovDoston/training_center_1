from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView

from .models import Course, Lesson, Module
from enrollments.models import Enrollment


def course_list(request):
    courses = Course.objects.with_full_counts().select_related("instructor__user")
    paginator = Paginator(courses, 12)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "page": page,
    }
    return render(request, "courses/course_list.html", context)


def course_detail(request, slug):
    modules_qs = Module.objects.with_lessons_count().prefetch_related("lessons")

    course = get_object_or_404(
        Course.objects.select_related("instructor__user").prefetch_related(
            Prefetch("modules", queryset=modules_qs)
        ),
        slug=slug,
    )

    modules = list(course.modules.all())
    modules_count = len(modules)
    lessons_count = sum(m.lessons_count for m in modules)

    is_enrolled = False
    if request.user.is_authenticated and hasattr(request.user, "student_profile"):
        is_enrolled = Enrollment.objects.filter(
            student=request.user.student_profile, course=course
        ).exists()

    # Find first lesson for the "Continue Learning" link
    first_lesson = None
    if modules:
        lessons = list(modules[0].lessons.all())
        if lessons:
            first_lesson = lessons[0]

    context = {
        "course": course,
        "modules_count": modules_count,
        "lessons_count": lessons_count,
        "is_enrolled": is_enrolled,
        "first_lesson": first_lesson,
    }
    return render(request, "courses/course_detail.html", context)


class LessonDetailView(LoginRequiredMixin, DetailView):
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
        # iterate course.modules.all -> module.lessons.all without N+1 queries.
        course = (
            Course.objects.prefetch_related(
                Prefetch(
                    "modules",
                    queryset=Module.objects.prefetch_related("lessons").order_by(
                        "order"
                    ),
                )
            )
            .select_related("instructor__user")
            .get(pk=course.pk)
        )

        # Build ordered lesson list from prefetched data (no extra query)
        all_lessons = []
        for module in course.modules.all():
            for les in module.lessons.all():
                all_lessons.append(les)

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
