from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm


def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    context = {"form": form}

    return render(request, "registration/signup.html", context)
