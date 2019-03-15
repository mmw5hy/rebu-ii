""" This file details all User models
"""

import datetime
from marketplace.models import Item
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class User(AbstractUser):
    """ The User class is set up as a superclass for Consumers and Producers

    Attributes:
        first_name: User's first name
        last_name: User's last name
        email: User's email
        address: User's primary address
        birthday: User's birthday
        is_producer: Bool dictating whether or not the user is a Producer
        is_admin: Bool dictating whether or not the user is an Admin

    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    address = models.CharField(max_length=300)
    birthday = models.DateField(default=datetime.date.today)
    is_producer = models.NullBooleanField(null=True)
    is_admin = models.NullBooleanField(default=False)

    def returnType(self):
        pass

    def get_full_name(self):
        """ Return "<first_name> <last_name> (<email>)"
        """
        return "%s %s (%s)" % (self.first_name, self.last_name, self.email)

    def get_short_name(self):
        """ Return just the User's name
        """
        return "%s %s" % (self.first_name, self.last_name)

    # def __str__(self):
    #     """ Return the full name
    #     """
    #     return get_full_name()

class Producer(User):
    """ The Producer is a User subclass that models any signed up producer

    Attributes:
        store_name: Producer's display name
        active: Bool dicating whether the Producer is active for Consumers to order from
        rating: Average of all item ratings for this Producer
        image: Producer's profile picture
        documents: Producer's documentation which the Admin will use to approve/disapprove
        processed: Bool dictating whether the Admin has approved/disapproved
        denied: Bool dictating whether this Producer was disapproved

    """
    store_name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    image = models.ImageField(upload_to="profile_pics", blank=False)
    documents = models.FileField(upload_to="producer_documents", blank=False)
    processed = models.BooleanField(default=False)
    denied = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.is_producer = True

    def returnType(self):
        return "Producer"


class Consumer(User):
    """ The Consumer is a User subclass that models any signed up consumer

    Attributes:
        favorite_producers: All Producers that the Consumer has favorited
    """
    favorite_producers = models.ManyToManyField(Producer, blank=True, default=[])
    favorite_items = models.ManyToManyField(Item, blank=True, default=[])

    USERNAME_FIELD = 'email'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.is_producer = False

    def returnType(self):
        return "Consumer"

    def get_fav_cooks(self):
        """Return space seperated list of consumer's favorite cooks"
        """
        if self.favorite_producers.all().count() == 0:
            return "No One Yet"
        else: 
            result = ""
            for e in self.favorite_producers.all():
                result += e.store_name + " "
            return result

    def get_fav_items(self ):
        """Return space seperated list of consumer's favorite items"
        """
        if self.favorite_items.all().count() == 0:
            return "Nothing Yet"
        else: 
            result = ""
            for e in self.favorite_items.all():
                result += e.name + " "
            return result

class Admin(User): # Admin user to approve producers
    """ The Admin class is a User subclass that can approve/disapprove Producers
    """

    USERNAME_FIELD = 'email'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self.is_producer = False # is not a producer

        def returnType(self):
            return "Admin"
