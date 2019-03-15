from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template.loader import render_to_string
from accounts.models import Consumer, Producer, User
from accounts.views import is_consumer
from django.shortcuts import redirect, reverse
from django_private_chat.models import Dialog, Message

from decimal import *
import hmac
import json
import os

from .models import Item, Order, OrderItem
from .viewsCart import add_item, clear_cart, create_cart, get_cart_or_none, get_valid_cart_items, get_valid_cart_order_items, get_order_item_from_cart, update_price

def item_page(request, item_id):
    """ Creates the item page to display an individual item.


    Args:
        request: The request calling this view.
        item_id: the id of the item to display

    """
    if not request.user.is_authenticated:
        return redirect('login')
    if not is_consumer(request.user):
        messages.error(request, 'Please log into a consumer account to place an order with Rebu.')
        return redirect('home')

    if request.method == "GET":
        item = Item.objects.get(pk=item_id)
        reviews = item.review_set.all()
        cart = get_cart_or_none(request)

        if request.user.is_authenticated and not request.user.is_producer and not request.user.is_admin:
            consumer = Consumer.objects.get(pk=request.user.id)
        else:
            consumer = None

        return render(request, 'order_item.html', {'cart': cart, 'item': item, 'reviews': reviews, 'consumer' : consumer})
    elif request.method == "POST":
        item = Item.objects.get(pk=item_id)
        consumer = request.user
        cart = get_cart_or_none(request)
        price = 0
        is_update = False
        if 'is_update' in request.POST and request.POST.get('is_update') == 'True':
            is_update = True
        if cart and not is_update:
            price = cart.price
        if is_update:
            order_items = []
            for pk, count in request.POST.items():
                if pk.isdigit() and count.isdigit():
                    pk = int(pk)
                    count = int(count)
                    order_item = get_order_item_from_cart(request, pk)
                    if order_item:
                        if is_update:
                            order_item.count = count
                        else:
                            order_item.count = order_item.count + count
                    else:
                        order_item = OrderItem(item_id=pk, count=count)
                    order_item.save()
                    order_items.append(order_item)
            create_cart(request, order_items, price, item.producer, consumer)
        else:
            add_item(cart, item, int(request.POST[item_id + ""]))
        messages.success(request, 'Cart successfully updated!')
        return redirect(reverse('item_specific', kwargs={'item_id': item_id}))

def all_items_page(request, producer_id):
    """ Creates the item page to display all items


    Args:
        request: The request calling this view.
        producer_id: the id of the producer to display

    """
    producer_id = int(producer_id)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        producer = Producer.objects.get(pk=producer_id)
        cart = get_cart_or_none(request)
        order_item_to_item = dict.fromkeys(get_valid_cart_order_items(request), None)
        for order_item, item in order_item_to_item.items():
            order_item_to_item[order_item] = Item.objects.get(pk=order_item.item_id)
        items_in_cart = set(get_valid_cart_items(request))
        items = []
        single = False
        for item in producer.item_set.all():
            if item.available:
                items.append(item)

        if request.user.is_authenticated and not request.user.is_producer and not request.user.is_admin:
            consumer = Consumer.objects.get(pk=request.user.id)
        else:
            consumer = None

        return render(request, 'order.html',
            {
            'cart': cart,
            'producer': producer,
            'items': items,
            'consumer' : consumer,
            })
    elif request.method == "POST":
        if request.POST.get('see_more'):
            return redirect(reverse('new_order', kwargs={'producer_id':producer_id}))
        producer = Producer.objects.get(pk=producer_id)
        consumer = request.user
        cart = get_cart_or_none(request)
        price = 0
        is_update = False
        if 'is_update' in request.POST and request.POST.get('is_update') == 'True':
            is_update = True
        if cart and not is_update:
            price = cart.price
        order_items = []
        for pk, count in request.POST.items():
            if pk.isdigit() and count.isdigit():
                pk = int(pk)
                count = int(count)
                order_item = get_order_item_from_cart(request, pk)
                if order_item:
                    if is_update:
                        order_item.count = count
                    else:
                        order_item.count = order_item.count + count
                else:
                    order_item = OrderItem(item_id=pk, count=count)
                order_item.save()
                order_items.append(order_item)
        if cart.producer_id != producer.id and not is_update and len(order_items):
            clear_cart(cart)
        create_cart(request, order_items, price, producer, consumer)
        return redirect(reverse('new_order', kwargs={'producer_id':producer_id}))


def producer_orders(request, order_id):
    """ Show a specific order for a producer to accept or decline


    Args:
        request: The request calling this view.
        order_id: the id of the order to display

    """
    order_id = int(order_id)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        order = Order.objects.get(pk=order_id)

        items = []
        for orderitem in order.items.all():
            items.append((orderitem.item, orderitem.count))

        return render(request, 'producer_orders.html',
            {
            'items': items,
            'order': order,
            'confirm': False,
            'past': False,
            })

    elif request.method == "POST":
        order = Order.objects.get(pk=order_id)
        d = Dialog(owner=order.producer, opponent=order.consumer)
        d.save()
        #d.owner = order.producer
        #d.opponent = order.consumer
        #m = Message()
        #m.sender = order.producer
        #m.dialog = d
        if request.POST.get('accept'):
            order.accepted = True
            temp = "Hello " + order.consumer.get_short_name() + " I've accepted your order. Thanks for ordering."
            m = Message(dialog=d, sender=order.producer, text=temp, read=False)
        else:
            order.completed = True
            order.accepted = False
            temp = "Hello " + order.consumer.get_short_name() + " I can't accomodate your order right now. Thanks for ordering."
            m = Message(dialog=d, sender=order.producer, text=temp, read=False)
        #d.save()
        m.save()
        order.save()
        return redirect('home')

def producer_confirm(request, order_id):
    """Show a specific order for a producer to accept or decline (confirming)


    Args:
        request: The request calling this view.
        order_id: the id of the order to display

    """
    order_id = int(order_id)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        order = Order.objects.get(pk=order_id)

        items = []
        for orderitem in order.items.all():
            items.append((orderitem.item, orderitem.count))

        return render(request, 'producer_orders.html',
            {
            'items': items,
            'order': order,
            'confirm': True,
            'past': False,
            })

    elif request.method == "POST":
        order = Order.objects.get(pk=order_id)
        order.completed = True
        order.save()
        return redirect('home')

def producer_past(request, order_id):
    """Past producers to display


    Args:
        request: The request calling this view.
        order_id: the id of the order to display

    """
    order_id = int(order_id)
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == "GET":
        order = Order.objects.get(pk=order_id)

        items = []
        for orderitem in order.items.all():
            items.append((orderitem.item, orderitem.count))

        return render(request, 'producer_orders.html',
            {
            'items': items,
            'order': order,
            'confirm': False,
            'past': True,
            })


def update_shopping_cart(request):
    """ Update the shopping cart


    Args:
        request: The request calling this view.
    """
    cart = get_cart_or_none(request)
    items = Item.objects.all().filter(producer_id=request.user.id)
    order_item_to_item = dict.fromkeys(get_valid_cart_order_items(request), None)
    if request.user.is_authenticated:
        if request.user.is_producer:
            if not items:
                empty_cart_msg = 'No items in your menu!'
            else:
                return {'items': items}
        else:
            if not cart or len(order_item_to_item) == 0:
                empty_cart_msg = 'No items in the shopping cart!'
            else:
                return {'order_item_to_item': order_item_to_item, 'cart': cart}
        return {'empty_cart_msg': empty_cart_msg}
    return {}

def order_checkout(request, producer_id):
    """ Checkout an order, make an order


    Args:
        request: The request calling this view.
        producer_id: id of the producer to order from
    """
    if request.method == 'GET':
        producer = Producer.objects.get(pk=producer_id)
        cart = get_cart_or_none(request)
        order_item_to_item = dict.fromkeys(get_valid_cart_order_items(request), None)
        if len(order_item_to_item) == 0:
            messages.error(request,'Add items to your cart before checking out!')
            return redirect(reverse('new_order', kwargs={'producer_id':producer.id}))
        for order_item, item in order_item_to_item.items():
            order_item_to_item[order_item] = Item.objects.get(pk=order_item.item_id)
        tax = Decimal(Decimal(0.06) * (cart.price + 5)).quantize(Decimal(".01"), rounding=ROUND_UP)
        total = float(Decimal(cart.price + 5 + tax).quantize(Decimal(".01"), rounding=ROUND_UP))
        tax = float(tax)
        return render(request, 'order_checkout.html',
            {
            'producer': producer,
            'order_item_to_item': order_item_to_item,
            'cart': cart,
            'tax': tax,
            'total': total,
            })
    elif request.method == 'POST':
        cart = get_cart_or_none(request)
        order = Order(price=cart.price, from_address=request.POST['from_address'], to_address=request.POST['to_address'], consumer_id=cart.consumer_id, producer_id=cart.producer_id)
        order.save()
        order.items.set(get_valid_cart_order_items(request))
        order.save()
        cart.items.clear()
        messages.error(request, 'Order placed successfully!')
        return redirect('home')


def past_order_page(request):
    """  Return the past orders for specific user


    Args:
        request: The request calling this view.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = request.user.id
    current_user = User.objects.get(pk=user_id)
    if current_user.is_producer:
        ret = Order.objects.filter(producer = current_user)
    else:
        ret = Order.objects.filter(consumer = current_user)
    items = []
    for order in ret:
        allItems = order.items.all()
        temp = []
        for item in allItems:
            temp.append(item.item.name)
        items.append(temp)

    incomplete_orders = []
    pending_orders = []
    past_orders = []
    for order in ret:
        if not order.completed:
            if order.accepted:
                pending_orders.append(order)
            else:
                incomplete_orders.append(order)
        else:
            past_orders.append(order)


    return render(request, 'past_orders.html', {'past_orders': past_orders, 'incomplete_orders': incomplete_orders, 'pending_orders': pending_orders, 'orders': ret})

#Get all Orders
def all_orders(request):
    d = {}
    if request.method != "GET":
        d["status"] = "FAILED"
        d["message"] = "MUST BE A GET REQUEST"
        return JsonResponse(d)

    queryset = Order.objects.all().values()

    arr = []
    for obj in queryset:
        arr.append(obj)
    if(len(queryset) > 0):
        d["status"] = "SUCCESS"
        d["data"] = arr
        return JsonResponse(d)
    else:
        d["status"] = "FAILED"
        d["message"] = "NO ORDERS AVAILABLE"
        return JsonResponse(d)

#Create new Order
def order_create(request, items, price, producer, consumer):
    d = {}
    if request.method != "POST":
        d["status"] = "FAILURE"
        d["message"] = "THE HTTP REQUEST MUST BE POST"
        return JsonResponse(d)

    if request.method == "POST":
        if (isValidOrder(request, price)):
            from_address = request.POST.get('from_address')
            to_address = request.POST.get('to_address')
            #info = request.POST.get('info')
            # user = request.POST.get('user')
            # user_num = int(user)
            # user = CustomUser.objects.filter(id=user_num)[0]
            # do other consumer_id and producer id stuff here
            newOrder = Order(from_address=from_address, to_address=to_address, completed=False, price=price, producer_id=producer.id, consumer_id=consumer.id)
            newOrder.save()
            for item in items:
                newOrder.items.add(item)
            newOrder.save()
            #for item_number in items.split(","):
            #    item_number = int(item_number)
            #    if (len(Item.objects.filter(id=item_number)) != 0):
            #        singleItem = Item.objects.filter(id=item_number)[0]
            #        newOrder.items.add(singleItem)
            #    else:
            #        d["status"] = "FAILED"
            #        d["message"] = "THAT ITEM DOESN'T EXIST"
            #        return JsonResponse(d,  status=404)

            d["id"] = newOrder.id
            d["status"] = "SUCCESS"
            d["message"] = "ORDER CREATED SUCCESSFULLY"
            return JsonResponse(d)
        else:
            d["status"] = "FAILURE"
            d["message"] = "ORDER SENT IS INVALID"
            return JsonResponse(d)


#Check if object is a valid Order
def isValidOrder (request, price):
    if (request.POST.get('from_address') and request.POST.get('to_address') and price != 0):
        # user_num = int(request.POST.get('user'))
        # if (len(CustomUser.objects.filter(id=user_num)) != 0):
        #    return True

        # do other consumer_id and producer id stuff here

        return True
    else:
        return False


# Get / Update / Delete a single order
def get_order(request, order):
    d = {}
    if request.method == "GET":
        order_num = int(order)
        if (len(Order.objects.filter(id=order_num)) != 0):
            singleOrder = Order.objects.filter(id=order_num).values()
            arr = []
            arr.append(singleOrder[0])
            d["status"] = "SUCCESS"
            d["data"] = arr
            return JsonResponse(d)
        else:
            d["status"] = "FAILED"
            d["message"] = "THAT ORDER DOESN'T EXIST"
            return JsonResponse(d)

    elif request.method == "POST":
        if (isValidOrder(request, request.POST.get('price'))):
            order_num = int(order)
            if (len(Order.objects.filter(id=order_num)) != 0):
                singleOrder = Order.objects.filter(id=order_num)[0]
                items = request.POST.get('items')
                singleOrder.from_address = request.POST.get('from_address')
                singleOrder.to_address = request.POST.get('to_address')
                singleOrder.completed = request.POST.get('completed')
                singleOrder.price = request.POST.get('price')
                # user = request.POST.get('user')
                # user_num = int(user)
                # user = CustomUser.objects.filter(id=user_num)[0]
                # do other consumer_id and producer id stuff here
                singleOrder.save()
                singleOrder.items.clear()
                for item_number in items.split(","):
                    item_number = int(item_number)
                    if (len(OrderItem.objects.filter(id=item_number)) != 0):
                        singleItem = OrderItem.objects.filter(id=item_number)[0]
                        singleOrder.items.add(singleItem)
                    else:
                        d["status"] = "FAILED"
                        d["message"] = "THAT ITEM DOESN'T EXIST"
                        return JsonResponse(d,  status=404)
                singleOrder.save()
                d["status"] = "SUCCESS"
                d["message"] = "ORDER UPDATED SUCCESSFULLY"
                return JsonResponse(d)

        d["status"] = "FAILED"
        d["message"] = "THAT ORDER DOESN'T EXIST"
        return JsonResponse(d,  status=404)

    elif request.method == "DELETE":
        order_num = int(order)
        if (len(Order.objects.filter(id=order_num)) == 0):
            d["status"] = "FAILED"
            d["message"] = "THAT ORDER DOESN'T EXIST"
            return JsonResponse(d,  status=404)
        singleOrder = Order.objects.filter(id=order_num)[0]
        singleOrder.delete()
        d["status"] = "SUCCESS"
        d["message"] = "Order DELETED SUCCESSFULLY"
        return JsonResponse(d)

    else:
        d["status"] = "FAILURE"
        d["message"] = "THE HTTP REQUEST MUST BE GET/POST/DELETE"
        return JsonResponse(d)
