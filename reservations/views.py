import datetime
from django.http import Http404
from django.views.generic import View
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import render, redirect, reverse
from rooms import models as room_models
from reviews import forms as review_forms
from . import models
from users import mixins as user_mixins


class CreateError(Exception):
    pass


class CreateReservationView(user_mixins.LoggedInOnlyView, View):
    def get(self, *args, **kwargs):
        room_pk = kwargs.get("room")
        year = kwargs.get("year")
        month = kwargs.get("month")
        day = kwargs.get("day")

        try:
            date_obj = datetime.datetime(year, month, day)
            room = room_models.Room.objects.get(pk=room_pk)
            models.BookedDay.objects.get(day=date_obj, reservation__room=room)
            raise CreateError()
        except room_models.Room.DoesNotExist:
            messages.error(self.request, _("Access denied."))
            return redirect(reverse("core:home"))
        except models.BookedDay.DoesNotExist:
            reservation = models.Reservation.objects.create(
                guest=self.request.user,
                room=room,
                check_in=date_obj,
                check_out=date_obj + datetime.timedelta(days=1),
            )
            return redirect(
                reverse("reservations:detail", kwargs={"pk": reservation.pk})
            )


class ReservationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        reservation = models.Reservation.objects.get_or_none(pk=pk)
        if not reservation or (
            reservation.guest != self.request.user
            and reservation.room.host != self.request.user
        ):
            raise Http404()
        form = review_forms.CreateReviewForm()
        return render(
            self.request,
            "reservations/detail.html",
            {"reservation": reservation, "form": form},
        )


def edit_reservation(request, pk, verb):
    reservation = models.Reservation.objects.get_or_none(pk=pk)
    if not reservation or (
        reservation.guest != request.user and reservation.room.host != request.user
    ):
        raise Http404()

    if verb == "confirm":
        reservation.status = models.Reservation.STATUS_CONFIRMED
    elif verb == "cancel":
        reservation.status = models.Reservation.STATUS_CANCELED
        models.BookedDay.objects.filter(reservation=reservation).delete()
    reservation.save()
    messages.success(request, _("Reservation Updated."))
    return redirect(reverse("reservations:detail", kwargs={"pk": reservation.pk}))
