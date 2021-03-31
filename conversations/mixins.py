from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, reverse


class ParticipantsOnlyView(UserPassesTestMixin):
    def test_func(self):
        conversation_pk = self.kwargs.get("pk")
        conversation = self.request.user.conversations.get_or_none(pk=conversation_pk)
        if conversation:
            return True

    def handle_no_permission(self):
        messages.error(self.request, _("You are not one of the participants 🤨"))
        return redirect(reverse("core:home"))
