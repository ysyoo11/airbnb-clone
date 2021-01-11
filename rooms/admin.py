from django.contrib import admin
from . import models


@admin.register(models.RoomType, models.Amenity, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    list_display = (
        "name",
        "used_in",
    )

    def used_in(self, obj):

        num_of_rooms = obj.rooms.count()

        if num_of_rooms == 1:
            return f"{num_of_rooms} room"
        else:
            return f"{num_of_rooms} rooms"


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """ Room Admin Definition """

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "name",
                    "description",
                    "country",
                    "city",
                    "price",
                    "address",
                )
            },
        ),
        (
            "Time",
            {
                "fields": (
                    "check_in",
                    "check_out",
                    "instant_book",
                )
            },
        ),
        (
            "Space",
            {
                "fields": (
                    "room_type",
                    "guests",
                    "beds",
                    "bedrooms",
                    "baths",
                )
            },
        ),
        (
            "More about the room",
            {
                "classes": ("collapse",),
                "fields": (
                    "amenities",
                    "house_rule",
                ),
            },
        ),
        ("Host", {"fields": ("host",)}),
    )

    ordering = ["price"]

    list_display = (
        "name",
        "country",
        "city",
        "price",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "count_amenities",
        "count_photos",
        "get_total_rating",
    )

    list_filter = (
        "instant_book",
        "host__superhost",
        "room_type",
        "amenities",
        "house_rule",
        "city",
        "country",
    )

    search_fields = (
        "=city",
        "^host__username",
    )

    filter_horizontal = (
        "amenities",
        "house_rule",
    )

    def count_amenities(self, obj):
        return obj.amenities.count()

    def count_photos(self, obj):
        return obj.photos.count()  # related name을 지정했기 때문에 photo_set 이 아니라 photos

    count_amenities.short_description = "Number of Amenities"


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """ Photo Admin Definition """

    pass