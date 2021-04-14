import os
import requests
import logging
from django.http import HttpResponse
from django.views.generic import FormView, DetailView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.core.files.base import ContentFile
from urllib.parse import urlencode
from config import settings
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    logout(request)
    messages.info(request, _("See you later!"))
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, SuccessMessageMixin, FormView):

    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    success_message = _("Welcome! 🎉")

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return HttpResponseRedirect(self.get_success_url())


def complete_verification(request, code):
    try:
        user = models.User.objects.get(email_code=code)
        user.email_verified = True
        user.email_code = ""
        user.save()
        # to do: add success message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get("GITHUB_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
    )


class GithubException(Exception):
    pass


def github_callback(request):
    try:
        client_id = os.environ.get("GITHUB_ID")
        client_secret = os.environ.get("GITHUB_SECRET2")
        code = request.GET.get("code", None)
        if code is not None:
            token_request = requests.post(
                f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                headers={"Accept": "application/json"},
            )
            token_json = token_request.json()
            error = token_json.get("error", None)
            if error is not None:
                raise GithubException("Can't get an access token.")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json",
                    },
                )
                profile_json = profile_request.json()
                username = profile_json.get("login", None)
                if username is not None:
                    name = profile_json.get("name")
                    email = profile_json.get("email")
                    bio = profile_json.get("bio")
                    try:
                        user = models.User.objects.get(email=email)
                        superuser = models.User.objects.get(
                            email=os.environ.get("SUPERUSER_EMAIL")
                        )
                        if user.login_method != models.User.LOGIN_GITHUB:
                            # When a user already has the account with other method
                            if user == superuser:
                                login(request, user)
                                messages.success(
                                    request, f"Welcome back, {user.first_name}!"
                                )
                                return redirect(reverse("core:home"))
                            else:
                                raise GithubException(
                                    f"Please log in with: {user.login_method}."
                                )
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,
                            first_name=name,
                            username=email,
                            bio=bio,
                            login_method=models.User.LOGIN_GITHUB,
                            email_verified=True,
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile.")
        else:
            raise GithubException("Can't get the code.")
    except GithubException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code", None)
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException("Can't get the authorization code.")
        else:
            access_token = token_json.get("access_token")
            profile_request = requests.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_json = profile_request.json()
            k_account = profile_json.get("kakao_account")
            email = k_account.get("email", None)
            if email is None:
                raise KakaoException("Please let me know your email address.")
            properties = profile_json.get("properties")
            nickname = properties.get("nickname")
            profile_image = properties.get("profile_image")
            try:
                user = models.User.objects.get(email=email)
                if user.login_method != models.User.LOGIN_KAKAOTALK:
                    raise KakaoException(f"Please log in with: {user.login_method}")
            except models.User.DoesNotExist:
                user = models.User.objects.create(
                    email=email,
                    username=email,
                    first_name=nickname,
                    login_method=models.User.LOGIN_KAKAOTALK,
                    email_verified=True,
                )
                user.set_unusable_password()
                user.save()
                if profile_image is not None:
                    photo_request = requests.get(profile_image)
                    user.avatar.save(
                        f"{nickname}_avatar", ContentFile(photo_request.content)
                    )
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


def google_login(request):
    client_id = os.environ.get("GOOGLE_ID")
    authorize_uri = "https://accounts.google.com/o/oauth2/v2/auth"
    redirect_uri = "http://127.0.0.1:8000/users/login/google/callback"
    scope = "https://www.googleapis.com/auth/userinfo.profile"
    query_string = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "token",
            "scope": scope,
        }
    )
    login_url = authorize_uri + "?" + query_string
    return redirect(login_url)


class GoogleException(Exception):
    pass


def google_callback(request):
    try:
        access_token = request.GET.get("access_token", None)
        print(access_token)
        client_id = os.environ.get("GOOGLE_ID")
        client_secret = os.environ.get("GOOGLE_SECRET")
        """ error """
        token_request = requests.get(
            f"https://accounts.google.com/o/oauth2/v2/auth/access_token?client_id={client_id}&client_secret={client_secret}&access_token={access_token}"
        )
        token_json = token_request.json()
        """ error """
        error = token_json.get("error", None)
        if error is not None:
            raise GoogleException("Can't get the authorization code.")
        else:
            access_token = token_json.get("access_token")
            profile_request = requests.get(
                "https://www.googleapis.com/auth/userinfo.profile",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_json = profile_request.json()
            email = profile_json.get("email", None)
            if email is None:
                raise GoogleException("Please let me know your email address.")
            try:
                user = models.User.objects.get(email=email)
                if user.login_method != models.User.LOGIN_GOOGLE:
                    raise GoogleException(f"Please log in with: {user.login_method}")
            except models.User.DoesNotExist:
                user = models.User.objects.create(
                    email=email,
                    username=email,
                    first_name=email,
                    login_method=models.User.LOGIN_GOOGLE,
                    email_verified=True,
                )
                user.set_unusable_password()
                user.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}!")
            return redirect(reverse("core:home"))
    except GoogleException as e:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):
    model = models.User
    template_name = "users/profile.html"
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    fields = (
        "avatar",
        "first_name",
        "last_name",
        "email",
        "gender",
        "bio",
        "date_of_birth",
        "language",
        "currency",
    )
    template_name = "users/user_update.html"
    success_message = "Profile updated 🙌🏼"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["email"].widget.attrs = {"placeholder": "Email address"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "Last name"}
        form.fields["bio"].widget.attrs = {"placeholder": "Bio"}
        form.fields["date_of_birth"].widget.attrs = {
            "placeholder": "Date of birth (YYYY-MM-DD)"
        }
        return form

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        self.object.username = email
        self.object.save()
        return super().form_valid(form)


class UpdatePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailUserOnlyView,
    SuccessMessageMixin,
    PasswordChangeView,
):
    template_name = "users/change-password.html"
    success_message = _("Password changed successfully.")

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm new password"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        translation.activate(lang)
        response = HttpResponse(200)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return response
