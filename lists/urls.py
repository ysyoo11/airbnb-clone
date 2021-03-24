from django.urls import path
from . import views

app_name = "lists"

urlpatterns = [
    path("toggle/<int:room_pk>", views.toggle_saving, name="toggle_saving"),
    path("my-lists/", views.SeeMyListsView.as_view(), name="my_lists"),
]
