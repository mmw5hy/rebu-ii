"""rebu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from django.conf.urls.static import static
from rebu import settings
from django_private_chat import urls as django_private_chat_urls

from marketplace import viewsCart, viewsItems, viewsOrders
from accounts import views as user_views
from reviews import views as review_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include('django_private_chat.urls')),
    url(r'^$', user_views.index, name='home'),

    # Items API
    url(r'^api/items/$', viewsItems.all_items),
    url(r'^api/items/create/$', viewsItems.item_create, name="create-item"),
    url(r'^api/items/(?P<item>[0-9]+)/$', viewsItems.get_item),
    url(r'^api/items/edit/$', viewsItems.update_item, name="edit-items"),

    # Orders API
    url(r'^api/orders/$', viewsOrders.all_orders),
    url(r'^api/orders/create/$', viewsOrders.order_create),
    url(r'^api/orders/(?P<order>[0-9]+)/$', viewsOrders.get_order),

    # Users API
    url(r'^api/consumers/$', user_views.all_consumers),
    url(r'^api/consumers/addFavProducer/(?P<producer_id>[0-9]+)$', user_views.add_fav_producer),
    url(r'^api/consumers/addFavItem/(?P<item_id>[0-9]+)$', user_views.add_fav_item),
    url(r'^api/consumers/removeFavProducer/(?P<producer_id>[0-9]+)$', user_views.remove_fav_producer),
    url(r'^api/consumers/removeFavItem/(?P<item_id>[0-9]+)$', user_views.remove_fav_item),
    # Reviews API
    url(r'^api/reviews/$', review_views.all_reviews),
    url(r'^api/reviews/create/$', review_views.review_create),
    url(r'^api/reviews/(?P<review>[0-9]+)/$', review_views.get_review),

    # Reviews Frontend
    url(r'^reviews/write/(?P<item_id>[0-9]+)/$', review_views.write_reviews),
    url(r'^orders/past/review/(?P<order_id>[0-9]+)/$', review_views.past_order_review, name='past_order_review'),

    # Signup
    url(r'^consumer/signup/', user_views.create_consumer_user, name='consumer-signup'),
    url(r'^producer/signup/', user_views.create_producer_user, name='producer-signup'),

    # Signin
    url(r'^login/', user_views.user_login, name='login'),
    url(r'^logout/', user_views.logout_view, name='logout'),

    # Order
    url(r'update_cart$', viewsCart.update_cart, name='update_cart'),
    url(r'^orders/new/item_page/(?P<item_id>[0-9]+)$', viewsOrders.item_page, name='item_specific'),
    url(r'^orders/new/(?P<producer_id>[0-9]+)/$', viewsOrders.all_items_page, name='new_order'),
    url(r'^orders/checkout/(?P<producer_id>[0-9]+)/$', viewsOrders.order_checkout, name='checkout_order'),
    url(r'^orders/edit/(?P<producer_id>[0-9]+)/remove_item/(?P<item_id>[0-9]+)/$', viewsCart.remove_item, name='remove_item'),

    # Past Orders
    url(r'^orders/past/$', viewsOrders.past_order_page, name='past_order_page'),

    # Consumer Profiles
    url(r'^consumer/profile/$', user_views.consumer_profile, name='consumer_profile'),
    url(r'^consumer/edit_profile/$', user_views.edit_consumer_profile, name='edit_consumer_profile'),
    url(r'^consumer/edit_success/$', user_views.consumer_edit_success, name='consumer_edit_success'),

    # Producer Profiles
    url(r'^producer/profile/$', user_views.producer_profile, name='producer_profile'),
    url(r'^producer/edit_profile/$', user_views.edit_producer_profile, name='edit_producer_profile'),
    url(r'^producer/edit_success/$', user_views.producer_edit_success, name='producer_edit_success'),

    # Admin
    url(r'^admin/producer/approval/(?P<producer_id>[0-9]+)/$', user_views.approval_page, name='producer_approval'),



    # Producer API
    url(r'^orders/(?P<order_id>[0-9]+)/$', viewsOrders.producer_orders, name='producer_orders'),
    url(r'^orders/past/(?P<order_id>[0-9]+)/$', viewsOrders.producer_past, name='producer_past'),
    url(r'^orders/confirm/(?P<order_id>[0-9]+)/$', viewsOrders.producer_confirm, name='producer_confirm'),




]
