"""
This file has all Cart API calls and update_cart and remove_item form
submission views
"""

from django.http import Http404, HttpResponse, JsonResponse
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template.loader import render_to_string
from accounts.models import Consumer, Producer
from accounts.views import is_consumer
from django.shortcuts import redirect, reverse
from django.contrib import messages

import os
import hmac
import json

from .models import Cart, Item, Order, OrderItem

def create_cart(request, order_items, price, producer, consumer):
    """ Creates or updates the user's cart.

    Creates a new cart for the user given the cart's fields.
    cart. If the cart already exists, the cart's fields are updated.

    Args:
        request: The request calling this view.
        order_items(marketplace.models.OrderItem): A list of the order items to be put in the cart
        price(int): The price of the cart
        producer(accounts.models.Producer): The producer this cart contains items from
        consumer(accounts.models.Consumer): The consumer this cart belongs to

    """

    d = {}
    if request.method != 'POST':
        d['status'] = 'FAILURE'
        d['message'] = 'THE HTTP REQUEST MUST BE POST'
        return JsonResponse(d)

    cart = get_cart_or_none(request)
    if cart and (not cart.producer_id or cart.producer_id != producer.id):
        cart.producer_id = producer.id
    price = 0
    cart.items.clear()
    for order_item in order_items:
        if order_item.count > 0:
            cart.items.add(order_item)
            price += order_item.count * order_item.item.price
    cart.price = price
    cart.save()
    messages.success(request, 'Cart successfully updated!')

def get_cart_or_none(request):
    """ Returns the user's cart.

    Returns the user's cart if it exists in the session. None if the user does not have a cart
    in the current session.

    Args:
        request: The request calling this view.

    """
    if not request.user.is_authenticated or request.user.is_superuser or request.user.is_producer or request.user.is_admin:
        return None

    if request.user.consumer is not None:
        try:
            cart = request.user.consumer.cart
        except ObjectDoesNotExist:
            return None

        if cart:
            try:
                return Cart.objects.get(pk=request.user.consumer.cart.id)
            except ObjectDoesNotExist:
                return None
    return None

def get_valid_cart_order_items(request):
    """ Returns all order items in the cart

    Returns a list of all order items that are currently in the user's cart.

    Args:
        request: The request calling this view.

    """
    cart = get_cart_or_none(request)
    if not cart:
        return []
    return list(cart.items.all().filter(count__gt=0))

def get_valid_cart_items(request):
    """ Returns all items in the cart

    Returns a list of all items that are currently in the user's cart.

    Args:
        request: The request calling this view.

    """
    order_items = get_valid_cart_order_items(request)
    return [Item.objects.get(pk=order_item.item_id) for order_item in order_items]

def get_order_item_from_cart(request, item):
    """ Gets a specific order item from the cart
If the given item exists in the cart, the corresponding OrderItem of that item
    is returned. None is returned otherwise

    Args:
        item (marketplace.models.Item): Item to check for

    """
    cart = get_cart_or_none(request)
    if not cart:
        return None
    order_items = get_valid_cart_order_items(request)
    for order_item in order_items:
        if order_item.item_id == item:
            return order_item
    return None

def clear_cart(cart):
    """ Empties a cart of all items

    All items within the cart are cleared, price is set to 0, and the producer
    is set to None

    Args:
        cart (marketplace.models.Cart): Cart to be cleared

    """
    cart.producer_id = None
    cart.price = 0
    cart.items.clear()
    cart.save()

def add_item(cart, item, count):
    """ Adds an Item to the Cart

    If the Item already exists within the Cart, the quantity is just
    incremented by count. If the Item does not exist, a new OrderItem object
    is created and added to the Cart. If the Producer is not the same as the
    Cart's Producer, the Cart's Producer is overwritten and the cart is cleared
    before adding the new item.

    Args:
        cart (marketplace.models.Cart): Cart for the item to be added to
        item (marketplace.models.Item): Item to be added
        count (int): Quantity of the item to be added

    """
    if (cart.producer_id != item.producer_id):
        clear_cart(cart)
        cart.producer_id = item.producer_id
        cart.save()

    try:
        order_item = cart.items.all().get(item_id=item.id)
        order_item.count += count
        order_item.save()
    except OrderItem.DoesNotExist:
        order_item = OrderItem(item_id=item.id, count=count)
        order_item.save()
        cart.items.add(order_item)
        cart.save()
    update_price(cart)
    return

def remove_item_from_cart(cart, item):
    """ Adds an Item to the Cart

    Removes the given item from the cart. IF CART DOES NOT HAVE ITEM,
    NO ERROR CHECKING IS CURRENTLY IMPLEMENTED.

    Args:
        cart (marketplace.models.Cart): Cart for the item to be removed from
        item (marketplace.models.Item): Item to be removed
    """
    if (cart.producer_id == item.producer_id):
        try:
            order_item = cart.items.all().get(item_id=item.id)
            cart.items.remove(order_item)
            update_price(cart)
        except:
            return

def remove_item(request, producer_id, item_id):
    """ Removes an item from the cart

    Removes the given item from the user's cart

    Args:
        request: The request calling this view.
        producer_id (int): The primary key value for the producer this item belongs to
        item_id (int): The primary key value for the item to be removed

    """
    item_id = int(item_id)
    cart = get_cart_or_none(request)
    if cart:
        for order_item in cart.items.all():
            if order_item.id == item_id:
                cart.items.remove(order_item)
                cart.save()
                order_item.delete()
                break
        update_price(cart)
    return redirect(request.META['HTTP_REFERER'])

def update_cart(request):
    """ Updates the items in the user's cart.

    Updates the items in the user's cart. All items to be added are passed as POST parameters.
    Updates the price to reflect the new total.

    Args:
        request: The request calling this view.

    """

    if request.method != "POST":
        redirect('home')
    if not is_consumer(request.user):
        messages.error(request, 'Log in as a customer to place an order with Rebu.')
        return redirect(request.META['HTTP_REFERER'])
    order_items = []
    for pk, count in request.POST.items():
        if pk.isdigit() and count.isdigit():
            pk = int(pk)
            count = int(count)
            order_item = get_order_item_from_cart(request, pk)
            order_item.count = count
            order_item.save()
    cart = get_cart_or_none(request)
    new_price = 0;
    for order_item in cart.items.all():
        if order_item.count == 0:
            cart.items.remove(order_item)
            order_item.delete()
        new_price += (order_item.item.price * order_item.count)
    cart.price = new_price
    cart.save()
    return redirect(request.META['HTTP_REFERER'])

def update_price(cart):
    """ Updates the cart price

    Updates the price of the cart to the given price.

    Args:
        price (int): New price of the cart

    """
    price = 0;
    for order_item in cart.items.all():
        price += (order_item.item.price * order_item.count)
    cart.price = price
    cart.save()
    return
