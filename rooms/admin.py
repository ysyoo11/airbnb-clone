from django.contrib import admin
from . import models


@admin.register(models.RoomType, models.Facility, models.Amenity, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    """ Item Admin Definition """

    pass


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
        "^city",
        "^host__username",
    )

    filter_horizontal = (
        "amenities",
        "house_rule",
    )

    def count_amenities(self, obj):
        print(len(obj.amenities.all()))
        return len(obj.amenities.all())

    count_amenities.short_description = "Number of Amenities"


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """ Photo Admin Definition """

    pass