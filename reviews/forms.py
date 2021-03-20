from django import forms
from . import models


class CreateReviewForm(forms.ModelForm):

    """ CreateReviewForm Definition """

    class Meta:
        model = models.Review
        fields = (
            "cleanliness",
            "accuracy",
            "communication",
            "location",
            "check_in",
            "value",
            "review",
        )

    def save(self):
        review = super().save(commit=False)
        return review
