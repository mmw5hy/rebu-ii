from django.test import TestCase, Client
import urllib.request
import urllib.parse
from django.core.files.uploadedfile import SimpleUploadedFile
import os.path

from marketplace.models import Item, Order, OrderItem, Cart
from accounts.models import Consumer, Producer

class OrderTestHere(TestCase):
    def setUp(self):
        """ Setup method that runs before each test """
        self.user = Consumer.objects.create(
            first_name='testuser',
            last_name='userLast',
            email='test@email.com',
            address='123 test drive',
            is_producer = False
        )
        self.user.set_password("123")
        self.user.username = "test@email.com"
        self.user.save()

        self.producer = Producer.objects.create(
            first_name='testuser',
            last_name='userLast',
            email='producer@email.com',
            address='123 test drive',
            store_name="Pete's shop",
            active=True,
            is_producer = True
        )
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, '../accounts/static/images/item-images/default_food_image.jpg')

        self.producer.image = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer.documents = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer.set_password("123")
        self.producer.username = "producer@email.com"
        self.producer.save()

        self.item = Item.objects.create(
            ingredients='cake, lemon',
            price='5.99',
            description='really great',
            rating=3.3,
            available=True,
            name="Cake",
            producer=self.producer,
            image="hi.png"
        )
        self.item.save()

        self.order = Order.objects.create(
            from_address='From Address',
            to_address='To Address',
            consumer_id=1,
            producer_id=1,
            completed=False,
            price=100
        )
        self.order.save()
        self.order.items.add(self.item.id)

        self.order_item = OrderItem.objects.create(
            count=3,
            item_id = self.item.id)
        self.order_item.save()
        self.order.items.add(self.order_item.id)
        self.order.save()

        self.cart = Cart.objects.create(
            consumer_id=1,
            producer_id=1,
            price=100)
        self.cart.items.add(self.order_item.id)
        self.cart.save()

        self.c = Client()

    def test_get_all_orders(self):
        """ Test to get all the orders that currently exist """
        self.response = self.c.get('/api/orders/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['from_address'], "From Address")

    def test_get_single_order(self):
        """ Test to get a single order that currently exists """
        self.response = self.c.get('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['id'], 1)
        self.assertEquals(self.data['data'][0]['from_address'], "From Address")

    def test_create_order(self):
        """ Test to create an order with all required fields."""
        self.c.post('/api/orders/1/', {
            'from_address': 'From Address',
            'to_address': 'To Address',
            'consumer_id': 1,
            'producer_id': 1,
            'completed': False,
            'price': 100,
            'items': [self.order_item.id]
            })
        self.response = self.c.get('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(self.data['data'][0]['id'], 1)
        self.assertEquals(self.data['data'][0]['from_address'], "From Address")
        self.assertEquals(self.data['data'][0]['to_address'], "To Address")

    def test_edit_single_order(self):
        """ Test to edit an order that currently exists."""
        self.c.post('/api/orders/1/', {
            'from_address': 'From Address2',
            'to_address': 'To Address2',
            'consumer_id': 1,
            'producer_id': 1,
            'completed': False,
            'price': 100,
            'items': [self.order_item.id]
            })
        self.response = self.c.get('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(self.data['data'][0]['id'], 1)
        self.assertEquals(self.data['data'][0]['from_address'], "From Address2")
        self.assertEquals(self.data['data'][0]['to_address'], "To Address2")

    def test_delete_single_order(self):
        """ Test to delete an order that currently exists."""
        self.response = self.c.delete('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.response = self.c.get('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")

    def test_shopping_cart(self):
        """ Test for existence of valid shopping cart. """
        cart = Cart.objects.all()
        self.assertEquals(len(cart), 1)

    def test_shopping_cart_checkout(self):
        """ Test checkout page functionality """
        client = Client()
        logged_in = client.login(username="test@email.com", password="123")
        self.assertTrue(logged_in)
        response = client.get('/orders/checkout/2/')
        self.assertEqual(response.status_code, 200)

    def test_edit_single_order_without_all_fields(self):
        """ Test to edit an order that currently exists without correctly specifying all fields."""
        self.c.post('/api/orders/1/', {
            'from_address': 'From Address2',
            'to_address': 'To Address2',
            'consumer_id': 1,
            'producer_id': 1,
            'completed': False,
            'price': 100,
            'items': [self.order_item.id]
            })

        self.c.post('/api/orders/1/', {
            'from_address': 'From Address2',
            'consumer_id': 1,
            'producer_id': 1,
            'completed': False,
            'price': 50,
            'items': [self.order_item.id]
            })
        self.response = self.c.get('/api/orders/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(self.data['data'][0]['id'], 1)    
        self.assertEquals(self.data['data'][0]['price'], '100.00')

    def test_delete_nonexistent_order(self):
        """ Test to delete an order that currently exists."""
        self.response = self.c.delete('/api/orders/2/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")
