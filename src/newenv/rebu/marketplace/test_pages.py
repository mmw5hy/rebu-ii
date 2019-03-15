from django.test import TestCase, Client
import urllib.request
import urllib.parse
from django.contrib.auth.models import AnonymousUser, User
from django.contrib import auth
from django_private_chat.models import Dialog, Message
from django.core.files.uploadedfile import SimpleUploadedFile
import os.path


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from marketplace.models import Cart, Item, Order, OrderItem
from accounts.models import Consumer, Producer
from accounts.models import Admin


class OrderTestHere(TestCase):
    def setUp(self):
        """ Setup items to test on """
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

        self.consumer = Consumer.objects.create(
            first_name='testuser',
            last_name='userLast',
            email='consumer@email.com',
            address='123 test drive',
            is_producer = False
        )
        self.consumer.set_password("123")
        self.consumer.username = "consumer@email.com"
        self.consumer.save()

        self.cart = Cart(consumer=self.consumer, producer=self.producer)
        self.cart.save()

        self.admin =Admin.objects.create(
        first_name = "admin",
        last_name = "admin",
        email = "admin@test.com",
        address = "admin",
        username = "admin@test.com",
        is_admin = True)

        self.admin.set_password("admin")

        self.admin.save()

        self.d = Dialog.objects.create(owner=self.admin, opponent=self.producer)
        self.d.save()
        intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
        self.m = Message.objects.create(dialog=self.d, sender=self.admin, text=intro, read=False)
        self.m.save()

        self.d2 = Dialog.objects.create(owner=self.admin, opponent=self.consumer)
        self.d2.save()
        intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
        self.m2 = Message.objects.create(dialog=self.d2, sender=self.admin, text=intro, read=False)
        self.m2.save()

        self.d3 = Dialog.objects.create(owner=self.producer, opponent=self.consumer)
        self.d3.save()
        curt = " I've accepted your order. Thanks for ordering."
        self.m3 = Message.objects.create(dialog=self.d3, sender=self.producer, text=curt, read=True)
        self.m3.save()

        self.c = Client()
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

        self.order_item = OrderItem.objects.create(
            item_id=1,
            count=5)
        self.order_item.save()
        self.cart.items.set([self.order_item])
        self.cart.save()

        self.order = Order.objects.create(
            from_address='From Address',
            to_address='To Address',
            consumer_id=1,
            producer_id=1,
            completed=False,
            price=100
        )
        self.order.save()

    # def test_past_orders_page_producer(self):
    #     """ Test past orders for a producer"""
    #     client = Client()
    #     client.login(username="producer@email.com", password="123")
    #     response = client.get('/orders/past/')
    #     self.assertEqual(response.status_code, 200)


    def test_past_orders_page_not_logged_in(self):
        """ Test past orders page if no one is logged in """
        client = Client()
        response = client.get("/orders/past")
        self.assertEqual(response.status_code, 301)

    def test_producer_orders(self):
        """ Test orders list for a producers """
        client = Client()
        client.login(username="producer@email.com", password="123")
        response = client.get('/orders/1/')
        self.assertEqual(response.status_code, 200)

    # def test_consumer_orders_checkout(self):
    #     """ Test checkout for an order"""
    #     client = Client()
    #     client.login(username="consumer@email.com", password="123")
    #     response = client.get('/orders/checkout/1/')
    #     self.assertEqual(response.status_code, 200)

    def test_get_all_producers_orders(self):
        """ Get all the orders that currently exist for producers """
        self.response = self.c.get('/api/orders/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['from_address'], "From Address")

    def test_consumer_signup_page(self):
        """ Test functionality of the consumer signup page """
        client = Client()
        response = client.get('/consumer/signup/')

        self.assertEqual(response.status_code, 200)

    def test_producer_signup_page(self):
        """ Test functionality of the producer signup page """
        client = Client()
        response = client.get('/producer/signup/')

        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        """ Test functionality of the login page """
        client = Client()
        response = client.get('/login/')

        self.assertEqual(response.status_code, 200)

    def test_consumer_login(self):
        """ Test consumer login functionality """
        client = Client()
        logged_in = client.login(username="consumer@email.com", password="123")
        self.assertTrue(logged_in)

    def test_producer_login(self):
        """ Test producer login functionality """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        self.assertTrue(logged_in)

    def test_consumer_logout(self):
        """ Test consumer logout functionality """
        client = Client()
        logged_in = client.login(username="consumer@email.com", password="123")
        logged_out = client.logout()

        user = auth.get_user(client)
        self.assertFalse(user.is_authenticated)

    def test_producer_logout(self):
        """ Test producer logout functionality """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        logged_out = client.logout()

        user = auth.get_user(client)
        self.assertFalse(user.is_authenticated)

    # def test_producer_dialogs_after_signup(self):
    #     """ Test dialogs page for a producer after signing up"""
    #     client = Client()
    #     client.login(username="producer@email.com", password="123")
    #     response = client.get('/dialogs/')
    #     self.assertEqual(response.status_code, 200)

    # def test_consumer_dialogs_after_signup(self):
    #     """ Test dialogs for a consumer after signing up"""
    #     client = Client()
    #     client.login(username="consumer@email.com", password="123")
    #     response = client.get('/dialogs/')
    #     self.assertEqual(response.status_code, 200)

    # def test_producer_admin_help_chat(self):
    #     """ Test admin help chat for a producer after signing up"""
    #     client = Client()
    #     client.login(username="producer@email.com", password="123")
    #     response = client.get('/dialogs/admin@test.com')
    #     self.assertEqual(response.status_code, 200)

    # def test_consumer_admin_help_chat(self):
    #     """ Test admin help chat for a consumer after signing up"""
    #     client = Client()
    #     client.login(username="producer@email.com", password="123")
    #     response = client.get('/dialogs/admin@test.com')
    #     self.assertEqual(response.status_code, 200)

    def test_num_dialogs_on_create(self):
        """ Test that only 3 precreated dialogues exist """
        diag = Dialog.objects.all()
        self.assertEquals(len(diag), 3)

    def test_consumer_admin_help_chat(self):
        """ Test that consumers have a dialog with admin that they don't own """
        diag = Dialog.objects.all()
        self.assertNotEquals(diag[0].owner, self.consumer)

    def test_producer_admin_help_chat(self):
        """ Test that producers have a dialog with admin that they don't own """
        diag = Dialog.objects.all()
        self.assertNotEquals(diag[1].owner, self.producer)

    def test_admin_help_chat_content(self):
        """ Test that message from admin to users is as intended """
        mess = Message.objects.all()
        self.assertEquals(mess[0].text, "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)")

    def test_num_messages_on_create(self):
        """ Test that only 3 precreated messages exist """
        mess = Message.objects.all()
        self.assertEquals(len(mess), 3)

    def test_producer_message_unread(self):
        """Test that message from admin to producer is unread"""
        mess = Message.objects.all()
        self.assertEquals(mess[0].read, False)

    def test_consumer_message_unread(self):
        """Test that message from admin to consumer is unread"""
        mess = Message.objects.all()
        self.assertEquals(mess[1].read, False)

    def test_user_message_read(self):
        """Test that message from producer to consumer is read"""
        mess = Message.objects.all()
        self.assertEquals(mess[2].read, True)

    def test_user_chat_content(self):
        """ Test that message from producer to consumer is as intended """
        mess = Message.objects.all()
        self.assertEquals(mess[2].text, " I've accepted your order. Thanks for ordering.")

    def test_producer_consumer_chat(self):
        """ Test that consumers have a dialog with producer that they don't own """
        diag = Dialog.objects.all()
        self.assertNotEquals(diag[2].owner, self.consumer)

    def test_producer_order_real(self):
        """ Test orders list for a producers """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logged_in)

    def test_producer_order_real_single(self):
        """ Test orders list for a producers """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/api/orders/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logged_in)


    def test_producer_order(self):
        """ Test orders list for a producers """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/orders/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logged_in)

    def test_producer_past_order(self):
        """ Test orders list for a producers """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/orders/past/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logged_in)

    def test_producer_past_order_confirm(self):
        """ Test orders list for a producers """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/orders/confirm/1/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(logged_in)

    def test_producer_profile_page(self):
        """ Test producer profile page """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/producer/profile/')
        self.assertEqual(response.status_code, 200)

    def test_producer_edit_profile_page(self):
        """ Test producer edit profile page """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/producer/edit_profile/')
        self.assertEqual(response.status_code, 200)

    def test_consumer_profile_page(self):
        """ Test consumer profile page """
        client = Client()
        logged_in = client.login(username="consumer@email.com", password="123")
        response = client.get('/consumer/profile/')
        self.assertEqual(response.status_code, 200)

    def test_consumer_edit_profile_page(self):
        """ Test consumer edit profile page """
        client = Client()
        logged_in = client.login(username="consumer@email.com", password="123")
        response = client.get('/consumer/edit_profile/')
        self.assertEqual(response.status_code, 200)

    def test_consumer_profile_page_not_logged_in(self):
        """ Test consumer profile page if no one is logged in """
        client = Client()
        response = client.get("/consumer/profile/")
        self.assertEqual(response.status_code, 302)

    def test_producer_successful_edit_page(self):
        """ Test producer successful edit profile page """
        client = Client()
        logged_in = client.login(username="producer@email.com", password="123")
        response = client.get('/producer/edit_success/')
        self.assertEqual(response.status_code, 200)

    def test_consumer_successful_edit_page(self):
        """ Test consumer successful edit profile page """
        client = Client()
        logged_in = client.login(username="consumer@email.com", password="123")
        response = client.get('/consumer/edit_success/')
        self.assertEqual(response.status_code, 200)

    def test_producer_successful_edit_page_not_logged_in(self):
        """ Test producer successful edit profile page if no one is logged in """
        client = Client()
        response = client.get('/consumer/edit_success/')
        self.assertEqual(response.status_code, 302)

    def test_consumer_successful_edit_profile_page_not_logged_in(self):
        """ Test consumer successful edit profile page if no one is logged in """
        client = Client()
        response = client.get("/consumer/edit_success/")
        self.assertEqual(response.status_code, 302)

"""
    def test_num_messages_producers(self):
        mess = Message.objects.all()
        self.assertEquals(len(mess), 2)


    def test_producer_admin_messages(self):
        diag = Dialog.objects.all()
        self.assertNotEquals(diag[1].owner, self.producer)
"""
