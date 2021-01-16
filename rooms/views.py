from django.shortcuts import render
from django.core.paginator import Paginator
from . import models


def all_rooms(request):
    page = request.GET.get("page")
    page_list = models.Room.objects.all()
    paginator = Paginator(page_list, 10, orphans=4)
    rooms = paginator.get_page(page)
    return render(request, "rooms/home.html", context={"page": rooms})
