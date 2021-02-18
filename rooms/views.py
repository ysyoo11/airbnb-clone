from django.http import Http404
from django.views.generic import ListView, DetailView, View, UpdateView
from django.shortcuts import render
from django.core.paginator import Paginator
from . import models, forms
from users import mixins as user_mixins


class HomeView(ListView):

    """ HomeView Definition """

    model = models.Room
    paginate_by = 20
    paginate_orphans = 4
    ordering = "created"
    context_object_name = "rooms"


class RoomDetailView(DetailView):

    """ RoomDetail Definition """

    model = models.Room


class SearchView(View):

    """ SearchView Definition """

    def get(self, request):

        country = request.GET.get("country")

        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():
                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                beds = form.cleaned_data.get("beds")
                bedrooms = form.cleaned_data.get("bedrooms")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                qs = models.Room.objects.filter(**filter_args).order_by("-created")

                paginator = Paginator(qs, 20, orphans=5)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)

                return render(
                    request,
                    "rooms/room_search.html",
                    {
                        "form": form,
                        "rooms": rooms,
                    },
                )

        else:
            form = forms.SearchForm()

        return render(request, "rooms/room_search.html", {"form": form})


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):

    """ EditRoomView Definition """

    model = models.Room
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "house_rule",
    )
    template_name = "rooms/room_edit.html"
    success_message = "Room updated ✨"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["name"].widget.attrs = {"placeholder": "Room name"}
        form.fields["description"].widget.attrs = {"placeholder": "Description"}
        form.fields["city"].widget.attrs = {"placeholder": "City"}
        form.fields["price"].widget.attrs = {"placeholder": "Price per night"}
        form.fields["address"].widget.attrs = {"placeholder": "Address"}
        form.fields["guests"].widget.attrs = {"placeholder": "Max number of guests"}
        form.fields["beds"].widget.attrs = {"placeholder": "Number of beds"}
        form.fields["bedrooms"].widget.attrs = {"placeholder": "Number of bedrooms"}
        form.fields["baths"].widget.attrs = {"placeholder": "Number of baths"}
        form.fields["check_in"].widget.attrs = {"placeholder": "Check-in time"}
        form.fields["check_out"].widget.attrs = {"placeholder": "Check-out time"}
        return form

    def form_valid(self, form):
        self.object.save()
        return super().form_valid(form)


class RoomPhotosView(user_mixins.LoggedInOnlyView, DetailView):

    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room
