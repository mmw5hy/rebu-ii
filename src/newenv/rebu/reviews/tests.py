from django.test import TestCase, Client
from .models import Review
from accounts.models import Consumer, Producer
from marketplace.models import Item
from django.core.files.uploadedfile import SimpleUploadedFile
import os.path


class ReviewTestCase(TestCase):

    def setUp(self):
        "Set up all the objects needed to test the review model"
        self.consumer = Consumer.objects.create(
            username="consumer_user",
            first_name="consumer_first_name",
            last_name="consumer_last_name",
            email="consumer@gmail.com",
            address="Consumer Address")

        self.consumer.set_password("consumer")
        self.consumer.save()

        self.consumer2 = Consumer.objects.create(
            username="consumer_user2",
            first_name="consumer_first_name2",
            last_name="consumer_last_name2",
            email="consumer@gmail.com2",
            address="Consumer Address2")

        self.consumer2.set_password("consumer2")
        self.consumer2.save()

        self.producer = Producer.objects.create(
            username="producer_user",
            first_name="producer_first_name",
            last_name="producer_last_name",
            email="producer@gmail.com",
            address="Producer Address")
        path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(path, '../accounts/static/images/item-images/default_food_image.jpg')

        self.producer.store_name="Producer Store"
        self.producer.active=False
        self.producer.image = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer.documents = SimpleUploadedFile(name='default_food_image.jpg', content=open(path, 'rb').read(), content_type='image/jpeg')
        self.producer.set_password("producer")

        self.producer.save()
        self.item = Item.objects.create(ingredients = "rice, lemon, everything nice", price = 5.99, description = "really good food", num_reviews = 1, rating = 3, available = True, name = 'food', producer = self.producer)

        # self.review1 = Review.objects.create(author = self.consumer, item = self.item, title = "delicious", body = "just as advertised", rating = 4)
        self.c = Client()
        self.response = self.c.post('/api/reviews/create/', {'author': '1', 'item': '1', 'title': 'really great cake!','rating': '3', 'body': 'pretty good, couldve been better'})

    def test_creation(self):
        "Make sure everything was created as planned"
        producer = Producer.objects.filter()
        self.assertEqual(len(producer), 1)

        consumer = Consumer.objects.filter()
        self.assertEqual(len(consumer), 2)

        item = Item.objects.filter(description = "really good food")
        self.assertEqual(len(item), 1)

        review = Review.objects.filter(title = "really great cake!")
        self.assertEqual(len(review), 1)

    def test_get_all_reviews(self):
        "Testing the get all reviews API endpoint"

        self.response = self.c.get('/api/reviews/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really great cake!")

    def test_get_all_reviews_fail(self):
        "Try to get all reviews as a post, should fail"

        self.response = self.c.post('/api/reviews/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")

    def test_get_single_review(self):
        "Testing getting a single review, by ID"

        self.response = self.c.get('/api/reviews/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really great cake!")


    def test_editing_review(self):
        "Trying to modify the object that is already in the database through API"

        self.response = self.c.post('/api/reviews/1/', {'author': '1', 'item': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})

        self.response = self.c.get('/api/reviews/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really terrible cake!")

    def test_delete_review(self):
        "Trying to delete the review object that we have created"

        self.response = self.c.delete('/api/reviews/1/')

        self.response = self.c.get('/api/reviews/1/')
        self.data = self.response.json()

        self.assertEquals(self.data['status'], "FAILED")

    def test_edit_review_without_all_fields_fail(self):
        "Trying to edit an already created review without specifying all fields returns failure"

        self.response = self.c.post('/api/reviews/1/', {'author': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILED")

    def test_edit_review_without_all_fields_no_change(self):
        "Trying to edit an already created review without specifying all fields should not change the review"

        self.response = self.c.post('/api/reviews/1/', {'author': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})
        self.response = self.c.get('/api/reviews/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really great cake!")

    def test_review_with_put_request_fail(self):
        "Calling get review with requests other than get, post, or delete should fail"

        self.response = self.c.put('/api/reviews/1/', {'author': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "FAILURE")

    def test_review_with_put_request_no_change(self):
        "Calling get review with requests other than get, post, or delete should not change the review object"

        self.response = self.c.put('/api/reviews/1/', {'author': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})
        self.response = self.c.get('/api/reviews/1/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really great cake!")

    def test_review_creation(self):
        "Makes sure that the review gets created properly"
        self.response = self.c.post('/api/reviews/create/', {'author': '1', 'item': '1', 'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})
        self.response = self.c.get('/api/reviews/2/')
        self.data = self.response.json()
        self.assertEquals(self.data['status'], "SUCCESS")
        self.assertEquals(len(self.data['data']), 1)
        self.assertEquals(self.data['data'][0]['title'], "really terrible cake!")

    def test_rating_before_reviews(self):
        "Makes sure that the item has a rating of 0 before any reviews are submitted"
        item = Item.objects.filter(id=1)[0]
        self.assertEquals(item.rating, 3)

    def test_rating_after_one_review(self):
        "Makes sure that the rating is correct after submitting one review"
        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        self.response = client.post('/reviews/write/1/', {'title': 'really terrible cake!','rating': '3', 'body': 'pretty good, couldve been better'})

        item = Item.objects.filter(id=1)[0]

        self.assertEqual(item.num_reviews, 1)
        self.assertEqual(item.rating, 3)

    def test_rating_edit(self):
        "Makes sure that if the same user submits a review for the same item the review is edited"
        client = Client()
        client.login(username=self.consumer.username, password="consumer")
        self.response = client.post('/reviews/write/1/', {'title': 'really terrible cake!','rating': '5', 'body': 'pretty good, couldve been better'})

        item = Item.objects.filter(id=1)[0]

        self.assertEqual(item.num_reviews, 1)
        self.assertEqual(item.rating, 5)

    def test_rating_after_two_reviews(self):
        "Makes sure that the rating updates properly when an additional review is submitted"
        client = Client()
        client.login(username=self.consumer2.username, password="consumer2")
        self.response = client.post('/reviews/write/1/', {'title': 'really terrible cake!','rating': '1', 'body': 'pretty good, couldve been better'})

        item = Item.objects.filter(id=1)[0]

        self.assertEqual(item.num_reviews, 2)
        self.assertEqual(item.rating, 2)
