from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from core import models as core_models


class Review(core_models.TimeStampedModel):

    """ Review Model Definition """

    review = models.TextField()
    cleanliness = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    accuracy = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    communication = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    location = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    check_in = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )
    value = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    user = models.ForeignKey(
        "users.User", related_name="reviews", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reviews", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.review

    def get_avg_rating(self):
        avg = (
            self.cleanliness
            + self.accuracy
            + self.communication
            + self.location
            + self.check_in
            + self.value
        ) / 6
        return round(avg, 2)

    get_avg_rating.short_description = "rating"

    class Meta:
        ordering = ("-created",)
