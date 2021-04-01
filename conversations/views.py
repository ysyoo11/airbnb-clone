from django.http import Http404
from django.shortcuts import redirect, reverse, render, resolve_url
from django.views.generic import View
from users import models as user_models
from reservations import models as reservation_models
from . import models, forms, mixins


def go_conversations(request, reservation_pk, a_pk, b_pk):
    reservation = reservation_models.Reservation.objects.get_or_none(pk=reservation_pk)
    try:
        user_one = user_models.User.objects.get(pk=a_pk)
        user_two = user_models.User.objects.get(pk=b_pk)
    except user_models.User.DoesNotExist:
        return None
    if user_one is not None and user_two is not None:
        try:
            conversation = models.Conversation.objects.get(reservation=reservation)
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create(reservation=reservation)
            conversation.participants.add(user_one, user_two)
    return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(mixins.ParticipantsOnlyView, View):

    """ ConversationDetailView Definition """

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        form = forms.AddCommentForm()
        return render(
            self.request,
            "conversations/conversation_detail.html",
            {
                "conversation": conversation,
                "reservation": conversation.reservation,
                "form": form,
            },
        )

    def post(self, *args, **kwargs):
        message = self.request.POST.get("message", None)
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404
        if message is not None:
            models.Message.objects.create(
                message=message, user=self.request.user, conversation=conversation
            )
        messages = list(conversation.messages.all())
        if len(messages) == 0:
            return redirect(reverse("conversations:detail", pk=pk))
        else:
            last_message = messages[-1]
            message_pk = last_message.pk
            return redirect(
                "{}#message_{}".format(
                    resolve_url("conversations:detail", pk=pk), message_pk
                )
            )
