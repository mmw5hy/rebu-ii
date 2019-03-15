from django.shortcuts import render
from .models import Review
from django.http import Http404, HttpResponse, JsonResponse
from accounts.models import Consumer
from marketplace.models import Item, Order
from .forms import ReviewForm
from django.contrib import messages
from django.shortcuts import redirect




# Create your views here.
def isValidReview (request):
    """ checks if a review is valid

        args:
            request: The request calling this view.
    """
    if (request.POST.get('author') and request.POST.get('item') and request.POST.get('title') and request.POST.get('body') and request.POST.get('rating')):
        # makes sure every field has something in it
        return True
    else:
        return False

def all_reviews(request):
    """ Returns all reviews in the database

        args:
            request: The request calling this view.
    """
    d = {}
    if request.method != "GET":
        d["status"] = "FAILED"
        d["message"] = "Must be a GET request!"
        return JsonResponse(d)

    queryset = Review.objects.all().values() # makes a queryset of all reviews

    arr = []
    for obj in queryset:
        arr.append(obj)
    if(len(queryset) > 0):
        d["status"] = "SUCCESS"
        d["data"] = arr
        return JsonResponse(d)
    else: # there's no reviews in the system
        d["status"] = "FAILED"
        d["message"] = "No Reviews Registered."
        return JsonResponse(d)


def review_create(request):
    """ API to create a new review
        args:
            request: The request calling this view.
    """
    d = {}
    if request.method != "POST": # A create request can only be a post request
        d["status"] = "FAILURE"
        d["message"] = "THE HTTP REQUEST MUST BE POST"
        return JsonResponse(d)

    if request.method == "POST": # if it is a post, extract info, validate, and create new review
        if (isValidReview(request)):
            author = request.POST.get('author')
            author = Consumer.objects.filter(id=author)[0]
            item = request.POST.get('item')
            item = Item.objects.filter(id=item)[0]
            title = request.POST.get('title')
            body = request.POST.get('body')
            rating = request.POST.get('rating')

            newReview = Review(author = author, item = item, title = title, body = body, rating = rating)
            newReview.save()
            d["id"] = newReview.id
            d["status"] = "SUCCESS"
            d["message"] = "REVIEW CREATED SUCCESSFULLY"
            return JsonResponse(d)
        else: # if the data sent is not valid, send error
            d["status"] = "FAILURE"
            d["message"] = "REVIEW SENT IS INVALID"
            return JsonResponse(d)

def get_review(request, review):
    """ Returns a specific review based on an id

        args:
            request: The request calling this view.
            review: the item id for the specific review
    """
    d = {}
    if request.method == "GET":
        item_num = int(review)
        if (len(Review.objects.filter(id=item_num)) != 0): # searches for a review with the specific id
            singleItem = Review.objects.filter(id=item_num).values()
            arr = []
            arr.append(singleItem[0])
            d["status"] = "SUCCESS"
            d["data"] = arr
            return JsonResponse(d) # return that one review
        else: # if we can't find the review, return an error
            d["status"] = "FAILED"
            d["message"] = "THAT ITEM DOESN'T EXIST"
            return JsonResponse(d)

    elif request.method == "POST": # if it's a post, we want to update the review
        if (isValidReview(request)):
            item_num = int(review)
        else:
            d["status"] = "FAILED"
            d["message"] = "INVALID ITEM FIELDS"
            return JsonResponse(d,  status=404)
        if (len(Review.objects.filter(id=item_num)) != 0): # find the individual review
            singleItem = Review.objects.filter(id=item_num)[0]
            author = request.POST.get('author')
            singleItem.author = Consumer.objects.filter(id=author)[0]
            item = request.POST.get('item')
            singleItem.item = Item.objects.filter(id=item)[0]
            singleItem.title = request.POST.get('title')
            singleItem.body = request.POST.get('body')
            singleItem.rating = request.POST.get('rating')
            #user = request.POST.get('user')
            #user_num = int(user)
            #user = CustomUser.objects.filter(id=user_num)[0]
            #singleItem.user = user
            singleItem.save()
            d["status"] = "SUCCESS"
            d["message"] = "ITEM UPDATED SUCCESSFULLY"
            return JsonResponse(d)
        d["status"] = "FAILED" # if the item doesn't exist, return an error
        d["message"] = "THAT ITEM DOESN'T EXIST"
        return JsonResponse(d,  status=404)

    elif request.method == "DELETE": # Dellete the speciic item_id that is mentioned in the form
        item_num = int(review)
        if (len(Review.objects.filter(id=item_num)) == 0): # return an error if the review doesn't exist
            d["status"] = "FAILED"
            d["message"] = "THAT ITEM DOESN'T EXIST"
            return JsonResponse(d,  status=404)
        singleItem = Review.objects.filter(id=item_num)[0]
        singleItem.delete()
        d["status"] = "SUCCESS"
        d["message"] = "ITEM DELETED SUCCESSFULLY"
        return JsonResponse(d)

    else: # if the request method is anything other than that, return a failure
        d["status"] = "FAILURE"
        d["message"] = "THE HTTP REQUEST MUST BE GET/POST/DELETE"
        return JsonResponse(d)


def past_order_review(request, order_id):
    """ Provides all the items in an order so the user can write reviews

        args:
            request: The request calling this view.
            order_id: The id of the order we're modifying

    """
    order_id = int(order_id)
    if not request.user.is_authenticated: # if the user is not authenticated, redirect to login
        return redirect('login')
    if request.method == "GET":
        order = Order.objects.get(pk=order_id) # obtain the order

        items = []
        for orderitem in order.items.all(): # iterate over the order, and add individual items to the list
            items.append((orderitem.item, orderitem.count))

        return render(request, 'past_order_review.html', # return the items and order
            {
            'items': items,
            'order': order,
            })


def write_reviews(request, item_id):
    """ Responsible for the page to write reviews for  a specific item
        args:
            request: The request calling this view.
            item_id: The id of the item we are writing a review for
    """
    if request.method == "GET": # if it's a get request, just return the review form
        form = ReviewForm()
        item = Item.objects.filter(id=item_id)[0]
        return render(request, 'write_review.html', {'form' : form, 'item_id' : item_id, 'item' : item})

    elif request.method == "POST": # if it's a post request, make an object from the form returned

        form = ReviewForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            body = form.cleaned_data['body']
            rating = form.cleaned_data['rating']
            item = Item.objects.filter(id=item_id)[0]
            author_id = request.user.id
            author = Consumer.objects.filter(id=author_id)[0]

            existing_review = Review.objects.filter(author = author, item = item)

            num_reviews = item.num_reviews
            curr_rating = item.rating

            if len(existing_review) == 0: # In the case that the consumer has not written a review for this item

                if num_reviews == 0: # increment the number of reviews for the item, and set the initial rating
                    item.num_reviews += 1
                    item.rating = rating
                    item.save()

                else: # if there's reviews for the item already, update the rating
                    item.num_reviews += 1
                    total_rating = int(curr_rating * num_reviews) + rating
                    item.rating = total_rating / item.num_reviews
                    item.save()

                newReview = Review(title = title, body = body, rating = rating, item = item, author = author) # save a new review
                newReview.save()

                messages.success(request, "Review was submitted successfully")

            else: # in the case that the consumer has written a review for this item
                """ We want to update the existing review from this user for this item """
                last_review = existing_review[0]

                total_rating = int(curr_rating * num_reviews) - last_review.rating + rating
                item.rating = total_rating / num_reviews
                item.save()

                last_review.rating = rating
                last_review.body = body
                last_review.title = title

                last_review.save()

                messages.success(request, "You have previously reviewed this item, review was edited successfully")

            # Need to update the rating for the individual producer

            producer = item.producer

            items_by_producer = Item.objects.filter(producer = producer, num_reviews__gt=0) # find the producer

            temp_total = 0

            for item in items_by_producer: # find all the items by this producer, sum up the ratings
                temp_total += item.rating

            producer.rating = temp_total / len(items_by_producer) # update the producer rating
            producer.save()

            return redirect('past_order_page')
