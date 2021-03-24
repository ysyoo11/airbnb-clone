from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView
from rooms import models as room_models
from users import mixins as user_mixins
from . import models


def toggle_saving(request, room_pk):
    action = request.GET.get("action", None)
    room = room_models.Room.objects.get_or_none(pk=room_pk)
    if room is not None and action is not None:
        the_list, created = models.List.objects.get_or_create(
            user=request.user, name="My Favourites"
        )
        if action == "add":
            the_list.rooms.add(room)
        elif action == "remove":
            the_list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class SeeMyListsView(user_mixins.LoggedInOnlyView, TemplateView):

    template_name = "lists/list_detail.html"
