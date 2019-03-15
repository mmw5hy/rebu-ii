from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib import messages
from .forms import ConsumerUserForm, ProducerUserForm, EditConsumerForm, EditProducerForm
from .models import Consumer, Producer, Admin, User
from django.contrib.auth import get_user_model, logout
from django_private_chat.models import Dialog, Message
import json

from marketplace.models import Cart, Item, Order

def index(request):
    """ Returns the home page, it's different for each type of user

        args:
            request: The request calling this view.
    """
    if request.user.is_authenticated:
        if request.user.is_producer:
            all_orders = Order.objects.all().filter(producer_id=request.user.id)
            incomplete_orders = []
            pending_orders = []
            past_orders = []
            for order in all_orders:
                if not order.completed:
                    if order.accepted:
                        pending_orders.append(order)
                    else:
                        incomplete_orders.append(order)
                else:
                    past_orders.append(order)
            return render(request, 'producer/homepage.html', {'past_orders': past_orders, 'incomplete_orders': incomplete_orders, 'pending_orders': pending_orders, 'orders': all_orders})

        # If the user is an admin, redirect them to the admin homepage with a list of producers that need to be approved/denied
        if request.user.is_admin:
            pending_producers = Producer.objects.filter(processed = False, denied = False)
            producers = []
            for prod in pending_producers:
                producers.append(prod)
            return render(request, 'admin/homepage.html', {'producers' : producers})

    if request.user.is_authenticated and not request.user.is_producer and not request.user.is_admin:
        consumer = Consumer.objects.get(pk=request.user.id)
    else:
        consumer = None

    return render(request, 'consumer/homepage.html', {'consumer': consumer, 'available_items': Item.objects.all().filter(available=True, producer__active=True, producer__processed=True), 'active_producers': Producer.objects.all().filter(active=True, processed=True)})

def check_admin_user(request):
    """Checks if the admin user exists, and creates one if it doesn't exist

        args:
            request: The request calling this view.
    """
    admin = Admin.objects.all()
    if len(admin) < 1:
        # There is no admin yet, so we have to make the account
        newAdmin = Admin.objects.create(first_name = "admin", last_name = "admin", email = "admin@test.com", address = "admin", username = "admin@test.com", is_admin = True)
        newAdmin.set_password("admin")

        newAdmin.save()

def user_login(request):
    """ Makes sure a login attempt has valid credentials, and logs in the user

        args:
            request: The request calling this view.
    """

    check_admin_user(request)
    if not request.user.is_authenticated:
        if request.method == "POST": # Check credentials if it's a post request
            username = request.POST.get('email', False)
            password = request.POST.get('password', False)
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request,'Login information is incorrect, try again!')
                return redirect('login.html')

        return render(request, 'login.html')
    else:
        return redirect('home')

def logout_view(request):
    """Logs out a user and redirects to home page

        args:
            request: The request calling this view.

    """
    logout(request)
    return redirect('home')

def create_consumer_user(request):
    """ Takes in post request, creates a new consumer user based on the information it contains, and precreates a help chat with admin

    args:
        request: The request calling this view.
"""
    if request.method == 'POST':
        current_username = request.POST.__getitem__('email')
        if Consumer.objects.filter(username=current_username).exists() or Producer.objects.filter(username=current_username).exists():
            messages.error(request,'An account with this email address already exists. Please use a different email.')
            return render(request, 'consumer/signup.html')
        form = ConsumerUserForm(request.POST)
        if form.is_valid(): # checks if the form is valid, and extracts the data
            consumer_user = Consumer(**form.cleaned_data)
            consumer_user.set_password(consumer_user.password)
            consumer_user.username = consumer_user.email
            consumer_user.save()
            cart = Cart(consumer_id=consumer_user.id)
            cart.save()
            consumer_user.cart = cart
            consumer_user.save()
            login(request, consumer_user)
            temp = Admin.objects.all()
            admin = temp.first()
            d = Dialog(owner=admin, opponent=consumer_user)
            d.save()
            intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
            m = Message(dialog=d, sender=admin, text=intro, read=False)
            m.save()
            return redirect('home')
        messages.error(request,'Signup unsuccessful. Please check information again.')
    return render(request, 'consumer/signup.html')

def consumer_edit_success(request):

    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'consumer/edit_success.html')

def producer_edit_success(request):

    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'producer/edit_success.html')

def create_producer_user(request):
    """ Takes in post request, creates a new consumer user based on the information it contains, and precreates a help chat with admin


    args:
        request: The request calling this view.
    """

    check_admin_user(request)
    if request.method == 'POST':
        current_username = request.POST.__getitem__('email')
        if Consumer.objects.filter(username=current_username).exists() or Producer.objects.filter(username=current_username).exists():
            messages.error(request,'An account with this email address already exists. Please use a different email.')
            return render(request, 'producer/signup.html')
        form = ProducerUserForm(request.POST, request.FILES)
        if form.is_valid():
            producer_user = Producer(**form.cleaned_data)
            producer_user.set_password(producer_user.password)
            producer_user.username = producer_user.email
            producer_user.image = request.FILES['image']
            producer_user.documents = request.FILES['documentation']
            producer_user.save()
            login(request, producer_user)
            temp = Admin.objects.all()
            admin = temp.first()
            d = Dialog(owner=admin, opponent=producer_user)
            d.save()
            intro = "Hello I'm the admin. Welcome to Rebu. Let me know if you have any questions :)"
            m = Message(dialog=d, sender=admin, text=intro, read=False)
            m.save()
            return redirect('home')
        messages.error(request,'Signup unsuccessful. Please check information again.')
    return render(request, 'producer/signup.html')

# API GET all Consumer models
def all_consumers(request):
    d = {}
    if request.method != "GET":
        d["status"] = "FAILED"
        d["message"] = "Must be a GET request!"
        return JsonResponse(d)

    queryset = Consumer.objects.all().values()

    arr = []
    for obj in queryset:
        arr.append(obj)
    if(len(queryset) > 0):
        d["status"] = "SUCCESS"
        d["data"] = arr
        return JsonResponse(d)
    else:
        d["status"] = "FAILED"
        d["message"] = "No Consumers Registered."
        return JsonResponse(d)

# API GET all Consumer models
def all_producers(request):
    d = {}
    if request.method != "GET":
        d["status"] = "FAILED"
        d["message"] = "Must be a GET request!"
        return JsonResponse(d)

    queryset = Producer.objects.all().values()

    arr = []
    for obj in queryset:
        arr.append(obj)
    if(len(queryset) > 0):
        d["status"] = "SUCCESS"
        d["data"] = arr
        return JsonResponse(d)
    else:
        d["status"] = "FAILED"
        d["message"] = "No Producers Registered."
        return JsonResponse(d)

def is_producer(user):
    """ Checks if a user is a producer"""
    return (not user.is_anonymous and \
            len(Producer.objects.filter(email=user.email)) != 0)

def is_consumer(user):
    """ Checks if a user is a consumer """
    return (not user.is_anonymous and \
            len(Consumer.objects.filter(email=user.email)) != 0)

def add_fav_producer(request, producer_id):
    """ Add favorite producer to consumer's favorite producer list """
    producer = Producer.objects.filter(id=producer_id)[0]
    consumer = request.user

    if is_consumer(consumer):
        consumer = Consumer.objects.filter(id=consumer.id)[0]
        consumer.favorite_producers.add(producer)
        consumer.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect("home")

def remove_fav_producer(request, producer_id):
    """ Remove a producer from a consumer's favorite producer list """
    producer = Producer.objects.filter(id=producer_id)[0]
    consumer = request.user

    if is_consumer(consumer):
        consumer = Consumer.objects.filter(id=consumer.id)[0]
        consumer.favorite_producers.remove(producer)
        consumer.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect("home")

def add_fav_item(request, item_id):
    """ Add favorite item to consumer's favorite item list"""
    item = Item.objects.filter(id=item_id)[0]
    consumer = request.user

    if is_consumer(consumer):
        consumer = Consumer.objects.filter(id=consumer.id)[0]
        consumer.favorite_items.add(item)
        consumer.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect("home")

def remove_fav_item(request, item_id):
    """ Add favorite item to consumer's favorite item list"""
    item = Item.objects.filter(id=item_id)[0]
    consumer = request.user

    if is_consumer(consumer):
        consumer = Consumer.objects.filter(id=consumer.id)[0]
        consumer.favorite_items.remove(item)
        consumer.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        return redirect("home")

def approval_page(request, producer_id):
    """ Approval page for admin users for a specific producer """
    producer = Producer.objects.filter(id=producer_id)[0]

    if request.method == 'GET':
        # If it is a get request, pass the one producer as a parameter
        return render(request, 'admin/approval.html', {'producer' : producer})

    elif request.method == 'POST':
        # If it is a post request, see if the producer was approved and edit their model
        action = request.POST['approve']

        if action == 'Approve':
            producer.processed = True
            producer.denied = False
            producer.save()
        elif action == 'Reject':
            producer.processed = True
            producer.denied = True
            producer.save()

        return redirect('home')

def consumer_profile(request):
    """  Return profile for logged in consumers

    Args:
        request: The request calling this view.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = request.user.id
    current_user = Consumer.objects.get(pk=user_id)
    if current_user.is_producer:
        return redirect('home')

    return render(request, 'consumer/profile.html', {'current_user': current_user})

def producer_profile(request):
    """  Return profile for logged in consumers

    Args:
        request: The request calling this view.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = request.user.id
    current_user = Producer.objects.get(pk=user_id)
    if current_user.is_producer:
        return render(request, 'producer/profile.html', {'current_user': current_user})
    else:
        return redirect('home')

def edit_consumer_profile(request):
    """  Return edit profile page for logged in consumers

    Args:
        request: The request calling this view.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = request.user.id
    current_user = Consumer.objects.get(pk=user_id)
    if current_user.is_producer:
        return redirect('home')

    if request.method == 'POST':
        form = EditConsumerForm(request.POST)
        if form.is_valid():
            consumer_user = Consumer(**form.cleaned_data)
            request.user.first_name = consumer_user.first_name
            request.user.last_name = consumer_user.last_name
            request.user.email = consumer_user.email
            request.user.birthday = consumer_user.birthday
            request.user.address = consumer_user.address
            request.user.save()
            return redirect('consumer_edit_success')
        messages.error(request,'Profile edit unsuccessful. Please check information again.')
    return render(request, 'consumer/edit_profile.html')


def edit_producer_profile(request):
    """  Return edit profile page for logged in producers

    Args:
        request: The request calling this view.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = request.user.id
    current_user = Producer.objects.get(pk=user_id)
    if not current_user.is_producer:
        return redirect('home')

    if request.method == 'POST':
        form = EditProducerForm(request.POST)
        if form.is_valid():
            producer_user = Producer(**form.cleaned_data)
            request.user.first_name = producer_user.first_name
            request.user.last_name = producer_user.last_name
            request.user.email = producer_user.email
            request.user.store_name = producer_user.store_name
            request.user.address = producer_user.address
            request.user.birthday = producer_user.birthday
            # request.user.image = producer_user.FILES['image']
            request.user.save()
            return redirect('producer_edit_success')
        messages.error(request,'Profile edit unsuccessful. Please check information again.')
    return render(request, 'producer/edit_profile.html')
