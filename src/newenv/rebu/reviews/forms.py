from django.forms import ModelForm
from .models import Review

class ReviewForm(ModelForm): # Form to create a review in the frontend
    class Meta:
        model = Review
        fields = ['title', 'body', 'rating']
