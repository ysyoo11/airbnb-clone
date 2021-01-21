from django import forms
from . import models


class LoginForm(forms.Form):

    """ LoginForm Definition """

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            models.User.objects.get(username=email)
            return email
        except models.User.DoesNotExist:
            raise forms.ValidationError(
                "Invalid email. Please check if your email is correct."
            )

    def clean_password(self):
        return "haha"