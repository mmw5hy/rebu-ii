from django.contrib import admin
from marketplace.models import Cart, Item, Order, OrderItem
from accounts.models import Consumer, Producer, Admin
from reviews.models import Review

admin.site.register(Cart)
admin.site.register(Item)
admin.site.register(Order)
admin.site.register(OrderItem)

admin.site.register(Consumer)
admin.site.register(Producer)
admin.site.register(Admin)

admin.site.register(Review)
