from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django_countries import countries
from . import models


class HomeView(ListView):

    """ HomeView Definition """

    model = models.Room
    paginate_by = 10
    paginate_orphans = 4
    ordering = "created"
    context_object_name = "rooms"


class RoomDetail(DetailView):

    """ RoomDetail Definition """

    model = models.Room


def search(request):
    city = request.GET.get("city", "Anywhere")
    city = city.title()
    if city == "":
        city = "Anywhere"
    country = request.GET.get("country", "AU")
    room_type = request.GET.get("room_type", 0)
    price = request.GET.get("price", 0)
    guests = request.GET.get("guests", 0)
    beds = request.GET.get("beds", 0)
    bedrooms = request.GET.get("bedrooms", 0)
    baths = request.GET.get("baths", 0)
    s_amenities = request.GET.getlist("amenities")
    instant = request.GET.get("instant", False)
    superhost = request.GET.get("superhost", False)

    form = {
        "city": city,
        "s_country": country,
        "s_room_type": int(room_type),
        "price": int(price),
        "guests": int(guests),
        "beds": int(beds),
        "bedrooms": int(bedrooms),
        "superhost": superhost,
        "s_amenities": s_amenities,
        "baths": int(baths),
        "instant": instant,
    }

    room_types = models.RoomType.objects.all()
    amenities = models.Amenity.objects.all()

    choices = {
        "countries": countries,
        "room_types": room_types,
        "amenities": amenities,
    }

    return render(request, "rooms/search.html", {**form, **choices})
