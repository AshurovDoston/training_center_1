from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from courses.models import Course
from profiles.models import Student

from .models import Enrollment


@login_required
@require_POST
def enroll_in_course(request, slug):
    """
    Enroll the current user in a course.

    Creates a Student profile if the user doesn't have one yet,
    then creates an Enrollment record. Silently handles the case
    where the user is already enrolled (redirect back to course).
    """
    course = get_object_or_404(Course, slug=slug)

    student, _created = Student.objects.get_or_create(user=request.user)

    Enrollment.objects.get_or_create(student=student, course=course)

    return redirect("course_detail", slug=course.slug)
