from django.db.models import Q
from django.shortcuts import redirect, reverse
from django.views.generic import DetailView
from users import models as user_models
from reservations import models as reservation_models
from . import models


def go_conversations(request, reservation_pk, a_pk, b_pk):
    reservation = reservation_models.Reservation.objects.get_or_none(pk=reservation_pk)
    user_one = user_models.User.objects.get_or_none(pk=a_pk)
    user_two = user_models.User.objects.get_or_none(pk=b_pk)
    if user_one is not None and user_two is not None:
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=user_one) & Q(participants=user_two)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create(reservation=reservation)
            conversation.participants.add(user_one, user_two)
    return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(DetailView):

    """ ConversationDetailView Definition """

    model = models.Conversation
