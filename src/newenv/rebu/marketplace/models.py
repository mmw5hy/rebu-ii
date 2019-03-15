""" This file details all Marketplace models
"""

from django.db import models
import datetime
from django.utils import timezone
from rebu.settings import MEDIA_ROOT

class Item(models.Model):
    """ The Item is a class that models any dish (Item)

    Attributes:
        name: Item's display name
        ingredients: Item's ingredients as a CharField
        price: Item's display price
        rating: Average of all item ratings for this Item
        num_reviews: Item's number of reviews
        description: Item's description as CharField
        available: Boll dictating if an Item is avilable to order
        producer: Item's producer that cooks the item
        image: Item's image to give idea of what dish looks like

    """
    name = models.CharField(max_length=30, blank=True)
    ingredients = models.CharField(max_length=1000, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_reviews = models.IntegerField(default = 0)
    description = models.CharField(max_length=300, blank=True)
    available = models.BooleanField(default=True)
    producer = models.ForeignKey('accounts.Producer', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="item-images", blank=False)

    def __str__(self):
        return self.name + " by " + str(self.producer_id)

class OrderItem(models.Model):
    """ The OrderItem is a class that models any item after it is ordered

    Attributes:
        item: Item that makes up an OrderItem
        count: number of item in previous argument included in OrderItem
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

class Cart(models.Model):
    """ The Cart is a class that models any cart object

    Attributes:
        items: Items that are in the cart
        price: Total price as a decimal of items in cart
        consumer: Consumer who the cart belongs to
        producer: Producer who will be cooking items in cart
    """
    items = models.ManyToManyField(OrderItem)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    consumer = models.OneToOneField('accounts.Consumer', on_delete=models.CASCADE)
    producer = models.ForeignKey('accounts.Producer', on_delete=models.CASCADE, blank=True, null=True)

class Order(models.Model):
    """ The Order is a class that models any order

    Attributes:
        items: Items that are in the order
        from_address: Address that the producer is delivering items from
        to_address: Address that the consumer is receiving items at
        consumer: Consumer who the order belongs to
        producer: Producer who will be cooking items in the order
        accepted: Bool dictating if an order has been accepted by the producer
        price: Total price as a decimal of items in cart
        created_at: DateTime that shows when an order was placed
    """
    items = models.ManyToManyField(OrderItem)
    from_address = models.CharField(max_length=1000, blank=True)
    to_address = models.CharField(max_length=1000, blank=True)
    consumer = models.ForeignKey('accounts.Consumer', on_delete=models.CASCADE)
    producer = models.ForeignKey('accounts.Producer', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.id)
