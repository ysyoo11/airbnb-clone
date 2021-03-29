from django import forms
from . import models
from django_countries.fields import CountryField


class SearchForm(forms.Form):

    """ SearchForm Definition"""

    city = forms.CharField(initial="Anywhere")
    country = CountryField(blank_label="(Select country)", blank=True).formfield()
    room_type = forms.ModelChoiceField(
        empty_label="Any kind", queryset=models.RoomType.objects.all(), required=False
    )
    price = forms.IntegerField(required=False)
    guests = forms.IntegerField(required=False)
    beds = forms.IntegerField(required=False)
    bedrooms = forms.IntegerField(required=False)
    baths = forms.IntegerField(required=False)
    instant_book = forms.BooleanField(required=False)
    superhost = forms.BooleanField(required=False)
    amenities = forms.ModelMultipleChoiceField(
        required=False,
        queryset=models.Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )


class CreatePhotoForm(forms.ModelForm):
    class Meta:
        model = models.Photo
        fields = ("file", "caption")

    def save(self, pk, *args, **kwargs):
        photo = super().save(commit=False)
        room = models.Room.objects.get(pk=pk)
        photo.room = room
        photo.save()


class CreateRoomForm(forms.ModelForm):
    class Meta:
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

    def save(self, *args, **kwargs):
        room = super().save(commit=False)
        return room
