from math import ceil
from django.shortcuts import render
from . import models


def all_rooms(request):
    page = request.GET.get("page", 1)
    page = int(page or 1)
    page_size = 10
    limit = page * page_size
    offset = limit - page_size
    max_page = ceil(models.Room.objects.count() / page_size)
    page_range = range(1, max_page + 1)
    all_rooms = models.Room.objects.all()[offset:limit]
    return render(
        request,
        "rooms/home.html",
        context={
            "rooms": all_rooms,
            "page": page,
            "max_page": max_page,
            "page_range": page_range,
        },
    )
