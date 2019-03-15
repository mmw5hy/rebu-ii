""" This file contains tests for Carts
"""

from decimal import Decimal
from django.test import TestCase, Client
import urllib.request
import urllib.parse

from accounts.models import Consumer, Producer
from marketplace.models import Item, OrderItem, Cart
from marketplace.viewsCart import add_item, clear_cart, update_price, remove_item_from_cart

class CartTestCases(TestCase):
    def setUp(self):
        # Set up all Consumer, Producer, Item, OrderItem, and Cart objects
        self.consumer1 = Consumer.objects.create(
            username="consumer1@email.com",
            first_name="consumer1_first_name",
            last_name="consumer1_last_name",
            email="consumer1@email.com",
            address="Consumer 1 Address")
        self.consumer1.save()

        self.consumer2 = Consumer.objects.create(
            username="consumer2@email.com",
            first_name="consumer2_first_name",
            last_name="consumer2_last_name",
            email="consumer2@email.com",
            address="Consumer 2 Address")
        self.consumer2.save()

        self.producer1 = Producer.objects.create(
            username="producer1username",
            first_name="Producer1FirstName",
            last_name="Producer1LastName",
            email="producer1@email.com",
            address="Producer 1 Address",
            store_name="Producer 1 Store Name",
            active=False)
        self.producer1.save()

        self.producer2 = Producer.objects.create(
            username="producer2username",
            first_name="Producer2FirstName",
            last_name="Producer2LastName",
            email="producer2@email.com",
            address="Producer 2 Address",
            store_name="Producer 2 Store Name",
            active=False)
        self.producer2.save()

        self.producer3 = Producer.objects.create(
            username="producer3username",
            first_name="Producer3FirstName",
            last_name="Producer3LastName",
            email="producer3@email.com",
            address="Producer 3 Address",
            store_name="Producer 3 Store Name",
            active=False)
        self.producer3.save()

        self.item1 = Item.objects.create(
            name="Item 1 Name",
            ingredients="Ingredients 1",
            price=2.00,
            rating=3.0,
            description="Item 1 Description",
            available=True,
            producer=Producer.objects.all().get(email="producer1@email.com"))
        self.item1.save()

        self.item2 = Item.objects.create(
            name="Item 2 Name",
            ingredients="Ingredients 2",
            price=1.00,
            rating=3.0,
            description="Item 2 Description",
            available=True,
            producer_id=Producer.objects.all().get(email="producer2@email.com").id)
        self.item2.save()

        self.item3 = Item.objects.create(
            name="Item 3 Name",
            ingredients="Ingredients 3",
            price=1.50,
            rating=4.0,
            description="Item 3 Description",
            available=True,
            producer_id=Producer.objects.all().get(email="producer2@email.com").id)
        self.item3.save()

        self.order_item1 = OrderItem.objects.create(
            item_id=1,
            count=5)
        self.order_item1.save()

        self.order_item2 = OrderItem.objects.create(
            item_id=2,
            count=3)
        self.order_item2.save()

        self.order_item3 = OrderItem.objects.create(
            item_id=3,
            count=5)
        self.order_item3.save()

        self.cart1 = Cart.objects.create(
            price=10.00,
            consumer=self.consumer1,
            producer=self.producer1)
        self.cart1.items.set([self.order_item1])
        self.cart1.save()

        self.cart2 = Cart.objects.create(
            price=10.50,
            consumer=self.consumer2,
            producer=self.producer2)
        self.cart2.items.set([self.order_item2, self.order_item3])
        self.cart2.save()

    def test_get_all_carts(self):
        """
        Test Cart.objects.all() and make sure all Cart objects were set up correctly
        """
        carts = Cart.objects.all()
        self.assertEqual(len(carts), 2)
        self.assertEqual(carts.get(id=1).price, 10.00)
        self.assertEqual(carts.get(id=1).consumer_id,
                         Consumer.objects.all().get(email="consumer1@email.com").id)
        self.assertEqual(carts.get(id=1).producer_id,
                         Producer.objects.all().get(email="producer1@email.com").id)
        self.assertEqual(carts.get(id=2).price, 10.50)
        self.assertEqual(carts.get(id=2).consumer_id,
                         Consumer.objects.all().get(email="consumer2@email.com").id)
        self.assertEqual(carts.get(id=2).producer_id,
                         Producer.objects.all().get(email="producer2@email.com").id)

    def test_single_item_within(self):
        """ Test that Cart with one OrderItem has proper fields """
        cart1 = Cart.objects.all().get(id=1)
        self.assertEqual(len(cart1.items.all()), 1)
        self.assertEqual(cart1.items.get().count, 5)
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).name,
                         "Item 1 Name")
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).ingredients,
                         "Ingredients 1")
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).price, 2.00)
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).rating, 3.00)
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).description,
                         "Item 1 Description")
        self.assertEqual(Item.objects.get(id=cart1.items.get().item_id).producer_id,
                         Producer.objects.all().get(email="producer1@email.com").id)

    def test_multiple_items_within(self):
        """ Test that Cart with multiple OrderItem has proper fields """
        cart2 = Cart.objects.all().get(id=2)
        self.assertEqual(len(cart2.items.all()), 2)
        self.assertEqual(cart2.items.get(id=2).count, 3)
        self.assertEqual(cart2.items.get(id=3).count, 5)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).name,
                         "Item 2 Name")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).ingredients,
                         "Ingredients 2")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).price, 1.00)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).rating, 3.00)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).description,
                         "Item 2 Description")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=2).item_id).producer_id,
                         Producer.objects.all().get(email="producer2@email.com").id)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).name,
                         "Item 3 Name")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).ingredients,
                         "Ingredients 3")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).price, 1.50)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).rating, 4.00)
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).description,
                         "Item 3 Description")
        self.assertEqual(Item.objects.get(id=cart2.items.get(id=3).item_id).producer_id,
                         Producer.objects.all().get(email="producer2@email.com").id)

    def test_get_cart_by_user(self):
        """ Test that Cart from Consumer.Cart is valid """
        consumer1_cart = Consumer.objects.all().get(email="consumer1@email.com").cart
        self.assertEqual(consumer1_cart.price, 10.00)
        consumer2_cart = Consumer.objects.all().get(email="consumer2@email.com").cart
        self.assertEqual(consumer2_cart.price, 10.50)

    def test_get_cart_by_item(self):
        """ Test querying for Cart by OrderItem """
        item1_orderitems = Item.objects.all().get(name="Item 1 Name").orderitem_set.all()
        self.assertEqual(len(item1_orderitems), 1)
        item1_cart = item1_orderitems.get().cart_set.all()
        self.assertEqual(len(item1_cart), 1)
        item2_orderitems = Item.objects.all().get(name="Item 2 Name").orderitem_set.all()
        self.assertEqual(len(item2_orderitems), 1)
        item2_cart = item2_orderitems.get().cart_set.all()
        self.assertEqual(len(item2_cart), 1)
        item3_orderitems = Item.objects.all().get(name="Item 3 Name").orderitem_set.all()
        self.assertEqual(len(item3_orderitems), 1)
        item3_cart = item3_orderitems.get().cart_set.all()
        self.assertEqual(len(item3_cart), 1)

    def test_clear_single_item_cart(self):
        """ Test clearing a cart with a single OrderItem """
        clear_cart(self.cart1)
        self.assertEqual(self.cart1.items.count(), 0)

    def test_clear_multiple_item_cart(self):
        """ Test clearing a cart with a multiple OrderItem """
        clear_cart(self.cart2)
        self.assertEqual(self.cart2.items.count(), 0)

    def test_add_existing_single_item(self):
        """ Test add_item API method for single Item already in Cart """
        self.assertEqual(self.cart1.items.get(item__name="Item 1 Name").count, 5)
        add_item(self.cart1, Item.objects.all().get(name="Item 1 Name"), 3)
        self.assertEqual(self.cart1.items.get(item__name="Item 1 Name").count, 8)
        self.assertEqual(self.cart1.price,
                         Item.objects.all().get(name="Item 1 Name").price * 8)

    def test_add_new_single_item(self):
        """ Test add_item API method for single Item not in Cart """
        add_item(self.cart1, Item.objects.all().get(name="Item 2 Name"), 3)
        self.assertEqual(self.cart1.items.get(item__name="Item 2 Name").count, 3)
        self.assertEqual(self.cart1.price,
                         Item.objects.all().get(name="Item 2 Name").price * 3)
        self.assertEqual(self.cart1.items.count(), 1)
        self.assertEqual(self.cart1.producer_id,
                         Item.objects.all().get(name="Item 2 Name").producer_id)

    def test_add_new_multiple_item(self):
        """ Test add_item API method for multiple Items not in Cart """
        add_item(self.cart1, Item.objects.all().get(name="Item 2 Name"), 3)
        add_item(self.cart1, Item.objects.all().get(name="Item 2 Name"), 2)
        add_item(self.cart1, Item.objects.all().get(name="Item 3 Name"), 1)
        self.assertEqual(self.cart1.items.count(), 2)
        self.assertEqual(self.cart1.items.get(item__name="Item 2 Name").count, 5)
        self.assertEqual(self.cart1.items.get(item__name="Item 3 Name").count, 1)
        self.assertEqual(self.cart1.price,
                         Item.objects.all().get(name="Item 2 Name").price * 5 +
                         Item.objects.all().get(name="Item 3 Name").price)

    def test_update_price_empty_cart(self):
        """ Test that update_price for an empty_cart is $0 """
        self.cart2.items.clear()
        self.assertEqual(self.cart2.items.count(), 0)
        update_price(self.cart2)
        self.assertEqual(self.cart2.price, Decimal(0.00))

    def test_update_price_edited_cart(self):
        """ Test that update_price for edited cart is correct """
        self.cart2.price = Decimal(0)
        self.assertEqual(self.cart2.price, 0)
        update_price(self.cart2)
        self.assertEqual(self.cart2.price, Decimal(10.50))

    def test_remove_single_item(self):
        remove_item_from_cart(self.cart1, Item.objects.all().get(name="Item 1 Name"))
        self.assertEqual(self.cart1.items.count(), 0)
        self.assertEqual(self.cart1.price, 0)

    def test_remove_non_existant_item(self):
        original_price = self.cart1.price
        remove_item_from_cart(self.cart1, Item.objects.all().get(name="Item 2 Name"))
        self.assertEqual(self.cart1.items.count(), 1)
        self.assertEqual(self.cart1.price, original_price)

    def test_add_item_from_different_producer(self):
        """ Test that ensures that adding an item from a different producer clears the cart from the previous producer. """
        add_item(self.cart1, Item.objects.get(pk=2), 1)
        self.assertEqual(self.cart1.items.count(), 1)
        self.assertEqual(self.cart1.price, 1.00)

    def test_add_item_from_multiple_different_producers(self):
        """ Test that ensures that adding an item from a different producer clears the cart from the previous producer. """
        add_item(self.cart1, Item.objects.get(pk=2), 1)
        add_item(self.cart1, Item.objects.get(pk=1), 1)
        self.assertEqual(self.cart1.items.count(), 1)
        self.assertEqual(self.cart1.price, 2.00)

    def test_clear_empty_cart(self):
        """ Test clearing a cart with no items """
        clear_cart(self.cart1)
        clear_cart(self.cart1)
        self.assertEqual(self.cart1.items.count(), 0)

    def test_cart_clears_with_multiple_items_from_different_producer(self):
        """ Test that ensures that adding an item from a different producer clears the cart of all items from the previous producer. """
        add_item(self.cart1, Item.objects.get(pk=2), 2)
        add_item(self.cart1, Item.objects.get(pk=3), 3)
        add_item(self.cart1, Item.objects.get(pk=1), 1)
        self.assertEqual(self.cart1.items.count(), 1)
        self.assertEqual(self.cart1.price, 2.00)

    def test_cleared_cart_has_no_producer(self):
        """ Test clearing a cart should disassociate it from the current producer. """
        clear_cart(self.cart1)
        self.assertEqual(self.cart1.producer_id, None)        


