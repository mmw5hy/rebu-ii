from django.http import Http404, HttpResponse, JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.template.loader import render_to_string
from accounts.forms import NewItemForm
from django.forms.models import model_to_dict
from django.shortcuts import redirect
from django.contrib import messages

import os
import hmac
import json

import urllib.parse
import urllib.request
from accounts.models import Consumer, Producer
from .models import Item, Order
from marketplace.models import Item

from accounts.views import is_producer

#Get all Items
def all_items(request):
    """ Returns all items that currently exist

    Returns all existing items as a Jsonresponse

    Args:
        request: The request calling this view.
    """
    d = {}
    if request.method != "GET":
        d["status"] = "FAILED"
        d["message"] = "MUST BE A GET REQUEST"
        return JsonResponse(d)

    queryset = Item.objects.all().values()

    arr = []
    for obj in queryset:
        arr.append(obj)
    if(len(queryset) > 0):
        d["status"] = "SUCCESS"
        d["data"] = arr
        return JsonResponse(d)
    else:
        d["status"] = "FAILED"
        d["message"] = "NO ITEMS AVAILABLE"
        return JsonResponse(d)


#Create new Item
def item_create(request):
    """ Returns all items that currently exist

    Returns all existing items as a JsonResponse

    Args:
        request: The request calling this view.
    """
    if not is_producer(request.user):
        return redirect('home')

    if request.method == "POST":
        new_item_form = NewItemForm(request.POST, request.FILES)
        if new_item_form.is_valid():
            new_item = Item(name=request.POST['name'],
                            ingredients=request.POST['ingredients'],
                            description=request.POST['description'],
                            price=request.POST['price'],
                            rating=0,
                            available=True,
                            image = request.FILES['image'],
                            producer_id=request.user.id)
            new_item.save()
            messages.error(request, new_item.name + " was successfully created!")
            return redirect('home')
    else:
        return render(request, 'create-item.html', {})

#Check if object is a valid Item
def isValidItem (request):
    """ Checks to see whether the item is valid

    Checks the request to ensure it has all required item fields. Returns true/false

    Args:
        request: The request calling this view.
    """
    if (request.POST.get('ingredients') and request.POST.get('price') and request.POST.get('description') and request.POST.get('rating') and request.POST.get('available') and request.POST.get('name') and request.POST.get('producer_id')):
        return True
    else:
        return False

def update_item(request):
    """ Updates an item's fields

    Updates the item's fields to the values given in request

    Args:
        request: The request calling this view.
    """
    if request.method == "POST":
        item = get_item(request, request.POST.get('item_id'))
        if request.POST.get('remove'):
            Item.objects.filter(id=request.POST.get('item_id')).delete()
            messages.error(request, item.name + ' was successfully deleted!')
        else:
            messages.error(request, item.name + ' was successfully edited!')
        return redirect('home')
    else:
        itemList = Item.objects.all().filter(producer_id=request.user.id)
        itemList = serializers.serialize('json', itemList)

        return render(request, 'edit-items.html', {'items': Item.objects.all().filter(producer_id=request.user.id), 'itemList': itemList})

# Get / Update / Delete a single item
def get_item(request, item):
    """ Returns the requested item

    Returns the item corresponding to the given primary key.
    If the method is a GET, the details of the item are returned.
    If the method is a POST, the item field's are updated to the ones provided in request.
    If the method is a DELETE, the item is deleted.


    Args:
        request: The request calling this view.
        item(count): The primary key of the desired item
    """
    d = {}

    #This is called when the user wants to 'view' an item
    if request.method == "GET":
        item_num = int(item)
        if (len(Item.objects.filter(id=item_num)) != 0):
            singleItem = Item.objects.filter(id=item_num).values()
            arr = []
            arr.append(singleItem[0])
            d["status"] = "SUCCESS"
            d["data"] = arr
            return JsonResponse(d)
        else:
            d["status"] = "FAILED"
            d["message"] = "THAT ITEM DOESN'T EXIST"
            return JsonResponse(d)

    #This is called when the user wants to update an item
    elif request.method == "POST":
        item_num = int(item)
        if (len(Item.objects.filter(id=item_num)) != 0):
            singleItem = Item.objects.filter(id=item_num)[0]
            singleItem.name = request.POST.get('name')
            singleItem.ingredients = request.POST.get('ingredients')
            singleItem.price = request.POST.get('price')
            singleItem.description = request.POST.get('description')
            if request.POST.get('available') is None:
                singleItem.available = False
            else:
                singleItem.available = True
                singleItem.save()
            singleItem.save()
            return singleItem

    #This is called when the user wants to delete an item
    elif request.method == "DELETE":
        item_num = int(item)
        if (len(Item.objects.filter(id=item_num)) == 0):
            d["status"] = "FAILED"
            d["message"] = "THAT ITEM DOESN'T EXIST"
            return JsonResponse(d,  status=404)
        singleItem = Item.objects.filter(id=item_num)[0]
        singleItem.delete()
        d["status"] = "SUCCESS"
        d["message"] = "ITEM DELETED SUCCESSFULLY"
        d["name"] = singleItem.name
        return JsonResponse(d)

    #All other HTTP requests will fail
    else:
        d["status"] = "FAILURE"
        d["message"] = "THE HTTP REQUEST MUST BE GET/POST/DELETE"
        return JsonResponse(d)
