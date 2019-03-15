from django.db import models
from accounts.models import Producer, Consumer
from marketplace.models import Item


class Review(models.Model):
    "Creates a model for submitting a review"
    author = models.ForeignKey(Consumer, on_delete=models.CASCADE) # foreign key to a consumer object
    item = models.ForeignKey(Item, on_delete=models.CASCADE) # foreign key to an Item
    title = models.CharField(max_length=50, blank=True) # Review has to have a title and a body
    body = models.TextField(blank=True)
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ) # A review should have a rating from 1-5
    rating = models.IntegerField(choices=RATING_CHOICES)
    time_written = models.DateTimeField(auto_now_add=True) # automatically adds a timestamp
