from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect, reverse


class EmailUserOnlyView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.error(
            self.request,
            f"Your account is linked with {self.request.user.login_method.title()} 🤨",
        )
        return redirect(reverse("core:home"))


class LoggedOutOnlyView(UserPassesTestMixin):
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.error(self.request, "Access is denied 😐")
        return redirect(reverse("core:home"))


class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy("users:login")