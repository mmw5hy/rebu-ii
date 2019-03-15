""" This file contains tests for accounts
"""

from accounts.models import Consumer, Producer, User, Admin
from marketplace.models import Item
from django.conf import settings
from django.test import RequestFactory, TestCase, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from .forms import ConsumerUserForm, ProducerUserForm, NewItemForm
from .views import all_consumers, all_producers, logout_view
from django.contrib import messages
import datetime
import os
import os.path
import json
from django.core.files.uploadedfile import SimpleUploadedFile


class AccountsTestCase(TestCase):

    def setUp(self):
        # Set up all consumers and producer objects to test
        self.consumer = Consumer.objects.create(
            username="consumer_user",
            first_name="consumer_first_name",
            last_name="consumer_last_name",
            email="consumer@gmail.com",
            address="Consumer Address")

        self.producer = Producer.objects.create(
            username="producer_user",
            first_name="producer_first_name",
            last_name="producer_last_name",
            email="producer@gmail.com",
            address="Producer Address")
        self.producer.store_name="Producer Store"
        self.producer.active=False
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, '../accounts/static/images/item-images/default_food_image.jpg')

        self.producer.image = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer.documents = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')

        self.producer.save()

        self.producer2 = Producer.objects.create(
            username="producer_user2",
            first_name="producer_first_name2",
            last_name="producer_last_name2",
            email="producer2@gmail.com",
            address="Producer Address 2")
        self.producer2.store_name="Producer Store 2"
        self.producer2.active=True
        self.producer2.image = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer2.documents = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')

        self.producer2.save()
        self.factory = RequestFactory()

        self.admin =Admin.objects.create(
            first_name = "admin",
            last_name = "admin",
            email = "admin@test.com",
            address = "admin",
            username = "admin@test.com",
            is_admin = True)

        self.admin.set_password("admin")
        self.producer.set_password("producer")
        self.producer.save()
        self.consumer.set_password("consumer")
        self.consumer.save()
        self.admin.save()

        self.item = Item.objects.create(ingredients='cake, lemon', price='5.99', description='eally great', rating=3.3, available=True, name="Cake", producer_id=1)
        self.item.save()

        SUCCESS = 25
        WARNING = 30
        ERROR = 40
        # d = Dialog(owner=self.admin, opponent=self.consumer)
        # d.save()
        # intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
        # m = Message(dialog=d, sender=self.admin, text=intro, read=False)
        # m.save()

        # d2 = Dialog(owner=self.admin, opponent=self.consumer)
        # d2.save()
        # intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
        # m2 = Message(dialog=d2, sender=self.admin, text=intro, read=False)
        # m2.save()

    def test_producer_favoriting(self):
        """ Ensure that favoriting proucers works properly"""
        cons = Consumer.objects.filter(first_name="consumer_first_name")[0]
        prod = Producer.objects.filter(first_name="producer_first_name")[0]

        cons.favorite_producers.add(prod)
        cons.save()

        self.assertEqual(cons.favorite_producers.count(), 1)

    def test_item_favoriting(self):
        """ Ensure that favoriting items works properly"""
        cons = Consumer.objects.filter(first_name="consumer_first_name")[0]
        item = Item.objects.filter(name="Cake")[0]

        cons.favorite_items.add(item)
        cons.save()

        self.assertEqual(cons.favorite_items.count(), 1)


    def test_admin_creation(self):
        """ Ensure that the admin was created correctly """
        admins = Admin.objects.all()
        self.assertEqual(len(admins), 1)

        admin = Admin.objects.get()
        self.assertEqual(admin.first_name, "admin")
        self.assertEqual(admin.last_name, "admin")
        self.assertEqual(admin.username, "admin@test.com")
        self.assertEqual(admin.email, "admin@test.com")
        self.assertEqual(admin.is_admin, True)


    def test_consumer_creation(self):
        """ Ensure that everything was created properly """
        consumers = Consumer.objects.all()
        self.assertEqual(len(consumers), 1)

        consumer = Consumer.objects.get()
        self.assertEqual(consumer.username, "consumer_user")
        self.assertEqual(consumer.first_name, "consumer_first_name")
        self.assertEqual(consumer.last_name, "consumer_last_name")
        self.assertEqual(consumer.email, "consumer@gmail.com")
        self.assertEqual(consumer.address, "Consumer Address")
        self.assertEqual(consumer.is_producer, False)

    def test_producer_creation(self):
        """ Ensure that everything was created properly """
        producers = Producer.objects.all()
        self.assertEqual(len(producers), 2)

        self.assertEqual(producers[0].first_name, "producer_first_name")
        self.assertEqual(producers[0].last_name, "producer_last_name")
        self.assertEqual(producers[0].email, "producer@gmail.com")
        self.assertEqual(producers[0].address, "Producer Address")
        self.assertEqual(producers[0].is_producer, True)
        self.assertEqual(producers[0].store_name, "Producer Store")
        self.assertEqual(producers[0].active, False)

        self.assertEqual(producers[1].first_name, "producer_first_name2")
        self.assertEqual(producers[1].last_name, "producer_last_name2")
        self.assertEqual(producers[1].email, "producer2@gmail.com")
        self.assertEqual(producers[1].address, "Producer Address 2")
        self.assertEqual(producers[1].is_producer, True)
        self.assertEqual(producers[1].store_name, "Producer Store 2")
        self.assertEqual(producers[1].active, True)

    def test_consumer_filter(self):
        """ Ensure filters work for consumers """
        cons = Consumer.objects.filter(first_name="consumer_first_name")
        self.assertEqual(len(cons), 1)
        self.assertEqual(cons.get().address, "Consumer Address")

    def test_producer_filter(self):
        """ Ensure that filters work for producers """
        prod = Producer.objects.filter(active=False)
        self.assertEqual(len(prod), 1)
        self.assertEqual(prod[0].store_name, "Producer Store")

        prod = Producer.objects.filter(active=True)
        self.assertEqual(len(prod), 1)
        self.assertEqual(prod[0].store_name, "Producer Store 2")

    def test_user_filter(self):
        """ Ensure the filters work across all users """
        users = User.objects.all()
        self.assertEqual(len(users), 4)

    def test_all_consumers(self):
        """ Tests that Consumers can be taken from requests """
        request = self.factory.get('')
        response = all_consumers(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data'][0]['username'], 'consumer_user')

    def test_all_producers(self):
        """ Tests that Producers can be taken from requests """
        request = self.factory.get('')
        response = all_producers(request)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['data'][0]['username'], 'producer_user')

    def test_all_producers_fail_for_post(self):
        """ Tests that Producers from POST fails """
        request = self.factory.post('')
        response = all_producers(request)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'FAILED')

    def test_all_consumers_for_no_consumers(self):
        """ Tests that no Consumers are reigstered """
        Consumer.objects.all().delete()
        request = self.factory.get('')
        response = all_consumers(request)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'FAILED')
        self.assertEqual(data['message'], 'No Consumers Registered.')

    def test_all_producers_for_no_producers(self):
        """ Tests that no Producers are reigstered """
        Producer.objects.all().delete()
        request = self.factory.get('')
        response = all_producers(request)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'FAILED')
        self.assertEqual(data['message'], 'No Producers Registered.')

    def test_admin_homepage(self):
        """ Test that the admin homepage renders correctly"""
        admin = Admin.objects.get()

        client = Client()
        client.login(username=admin.username, password="admin")
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_approval_page(self):
        """ Test that the approval page for a specific producer works"""
        producer = Producer.objects.all()[0]
        client = Client()
        client.login(username="admin@test.com", password="admin")
        response = client.get('/admin/producer/approval/2/')

        self.assertEqual(response.status_code, 200)

    def test_duplicate_consumer_creation(self):
        """ Ensure that a consumer account isn't created with the same email address """

        self.duplicate_consumer = Consumer.objects.create(
            username="duplicate_consumer_user",
            first_name="duplicate_consumer_first_name",
            last_name="consumer_last_name",
            email="duplicate_consumer@gmail.com",
            address="Duplicate Consumer Address")

        self.duplicate_consumer.delete()
        cons = Consumer.objects.filter(first_name="duplicate_consumer_first_name")

    def test_duplicate_producer_creation(self):
        """ Ensure that a producer account isn't created with the same email address """

        self.duplicate_producer = Producer.objects.create(
            username="duplicate_producer_user",
            first_name="duplicate_producer_first_name",
            last_name="duplicate_producer_last_name",
            email="duplicate_producer@gmail.com",
            address="Duplicate Producer Address")
        self.duplicate_producer.store_name="Duplicate Producer Store"
        self.duplicate_producer.active=False
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, '../accounts/static/images/item-images/default_food_image.jpg')

        self.duplicate_producer.image = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.duplicate_producer.documents = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')

        self.duplicate_producer.save()
        self.duplicate_producer.delete()

        prod = Producer.objects.filter(first_name="duplicate_producer_first_name")
        self.assertEqual(len(prod), 0)

    def test_add_fav_producer(self):
        """ Make sure that adding favorite producer works """

        prod_id = self.producer.id

        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        request = client.get("/api/consumers/addFavProducer/" + str(prod_id))

        self.assertEqual(len(self.consumer.favorite_producers.all()), 1)
        self.assertEqual(request.status_code, 302)

    def test_add_fav_item(self):
        """ Make sure that adding favorite items works"""

        item_id = self.item.id

        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        request = client.get("/api/consumers/addFavItem/" + str(item_id))

        self.assertEqual(len(self.consumer.favorite_items.all()), 1)
        self.assertEqual(request.status_code, 302)

    def test_add_fav_producer_twice(self):
        """ Make sure nothing weird happens if we try to add the same producer to favorites twice"""

        prod_id = self.producer.id

        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        request = client.get("/api/consumers/addFavProducer/" + str(prod_id))
        request2 = client.get("/api/consumers/addFavProducer/" + str(prod_id))


        self.assertEqual(len(self.consumer.favorite_producers.all()), 1)
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request2.status_code, 302)

    def test_add_new_item_twice(self):
        """ Make sure nothing weird happens if we try to add the same item to favorites twice"""

        item_id = self.item.id

        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        request = client.get("/api/consumers/addFavItem/" + str(item_id))
        request2 = client.get("/api/consumers/addFavItem/" + str(item_id))

        self.assertEqual(len(self.consumer.favorite_items.all()), 1)
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request2.status_code, 302)

    def test_add_fav_producer_in_producer_mode(self):
        """ Make sure we fail gracefully if we try to add a producer to favorites while logged into a producer account"""

        prod_id = self.producer.id

        client = Client()
        client.login(username=self.producer.username, password="producer")
        request = client.get("/api/consumers/addFavProducer/" + str(prod_id))

        self.assertEqual(len(self.consumer.favorite_producers.all()), 0)
        self.assertEqual(request.status_code, 302)

    def test_edit_consumer_first_name(self):
        """ Make sure we can save a change to the consumer's first name"""
        client = Client()
        self.assertEqual(self.consumer.first_name, "consumer_first_name")
        self.consumer.first_name = "new_consumer_first_name"
        self.assertEqual(self.consumer.first_name, "new_consumer_first_name")

    def test_success_message_notif(self):
        """ Make sure django message API actually displays a green/success message"""
        request = self.factory.get('')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, 'This is a success message!', messages)

        for message in messages:
            self.assertEqual(message.level, SUCCESS)

    def test_error_message_notif(self):
        """ Make sure django message API actually displays a red/error message"""
        request = self.factory.get('')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, 'This is an error message!', messages)

        for message in messages:
            self.assertEqual(message.level, ERROR)

    def test_warning_message_notif(self):
        """ Make sure django message API actually displays a yellow/warning message"""
        request = self.factory.get('')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, 'This is a warning message!', messages)

        for message in messages:
            self.assertEqual(message.level, WARNING)

    def test_incorrect_login_message(self):
        """ Make sure django releases an error when logging in with incorrect credentials"""
        request = self.factory.get('')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, 'Incorrect Login Information!', messages)

        client = Client()
        client.login(username="wrong_username", password="consumer")

        for message in messages:
            self.assertEqual(message.level, ERROR)

    def test_correct_login_message(self):
        """ Make sure django releases a success message when logging in with correct credentials"""
        request = self.factory.get('')
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, 'Incorrect Login Information!', messages)

        client = Client()
        client.login(username=self.consumer.username, password="consumer")

        for message in messages:
            self.assertEqual(message.level, SUCCESS)

#     def test_new_item_form(self):
#         post_data = {
#             'name':"food",
#             'ingredients':"tomatoes",
#             'description':"delicious",
#             'price':2.3,
#         }
#         upload_file = open(os.path.join(settings.MEDIA_ROOT,
#                                         "item-images/default_food_image.jpg"),
#                            'rb')
#         file_data = {
#             'image': upload_file,
#         }
#         form = NewItemForm(post_data, file_data)
#         self.assertTrue(form.is_valid())
