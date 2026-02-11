from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    age = forms.IntegerField(required=False, min_value=1)
    phone = forms.CharField(required=False, max_length=15)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "age", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ### Clear help texts for all fields
        for field in self.fields.values():
            field.help_text = ""

        # ### Clear help texts for specific fields
        # self.fields["username"].help_text = ""
        # self.fields["password1"].help_text = ""

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Bunday email manzili allaqachon ro'yxatdan o'tgan."
            )
        return email

    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.email = self.cleaned_data["email"]
    #     if commit:
    #         user.save()
    #     return user
