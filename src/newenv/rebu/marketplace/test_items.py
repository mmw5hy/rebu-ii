from django.test import TestCase, Client, RequestFactory
import urllib.request
import urllib.parse
from django.contrib.auth.models import AnonymousUser, User

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from marketplace.models import Item, Order
from accounts.models import Consumer, Producer

class OrderTestHere(TestCase):
    def setUp(self):
        """ Setup items to test on """
        self.factory = RequestFactory()
        self.user = Producer.objects.create(first_name='testuser', last_name='userLast', email='test@email.com', address='123 test drive', store_name="Pete's shop", active=True)
        self.user.set_password("123")
        self.user.username = "test@email.com"
        self.user.save()
        self.c = Client()
        self.item = Item.objects.create(ingredients='cake, lemon', price='5.99', description='eally great', rating=3.3, available=True, name="Cake", producer_id=1)
        self.item.save()

    def test_get_all_items(self):
        """ Get all the items that currently exist """
        self.response = self.c.get('/api/items/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['name'], "Cake")

    def test_get_single_item(self):
        """ Get a single item that currently exists """
        self.response = self.c.get('/api/items/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['id'], 1)

    def test_edit_single_item(self):
        """ Edit a single item that currently exists """
        self.item.price = 6.99
        self.item.save()

        self.response = self.c.get('/api/items/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['price'], '6.99')

    def test_get_id(self):
        """ Get a single item that currently exists """
        self.response = self.c.get('/api/items/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['data'][0]['id'], 1)

    def test_delete_single_item(self):
        """ Delete a single item that currently exists """
        self.c.delete('/api/items/1/')
        self.response = self.c.get('/api/items/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")

    def test_get_single_item(self):
        """ Get a single item that currently exists """
        self.response = self.c.get('/api/items/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['id'], 1)

    def test_get_nonexistent_item_fail(self):
        """ Edit a single item that currently exists """
        self.response = self.c.get('/api/items/2/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")
        self.assertEquals(self.data['message'], "THAT ITEM DOESN'T EXIST")
