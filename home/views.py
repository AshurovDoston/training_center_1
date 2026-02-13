from django.shortcuts import render

# Import the Course model so we can show featured courses on the home page.
# Course.objects gives us access to CourseManager, which has with_full_counts().
from courses.models import Course


def home_view(request):
    """
    Home page view — shows a hero section, featured courses, and a CTA.

    We fetch up to 3 courses to display as "featured" on the home page.
    with_full_counts() annotates each course with modules_count, lessons_count,
    and enrollments_count so the template can display those stats.
    select_related("instructor__user") joins the instructor and user tables
    in a single query to avoid extra database hits.
    [:3] limits the result to 3 courses (Python slice notation).
    """
    featured_courses = Course.objects.with_full_counts().select_related(
        "instructor__user"
    )[:4]
    content = {
        "featured_courses": featured_courses,
    }
    return render(request, "home.html", content)
