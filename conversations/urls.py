from django.urls import path
from . import views

app_name = "conversations"

urlpatterns = [
    path("", views.ConversationsListView.as_view(), name="list"),
    path(
        "go/<int:reservation_pk>/<int:a_pk>/<int:b_pk>/",
        views.go_conversations,
        name="go",
    ),
    path("<int:pk>/", views.ConversationDetailView.as_view(), name="detail"),
]
